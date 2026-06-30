import time
import os
import asyncio
import sys
import json
import logging
import tempfile
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.document import Document
from app.models.query_log import QueryLog


logger = logging.getLogger(__name__)
settings = get_settings()

MEDICAL_SYSTEM_PROMPT = """你是一个专业的医疗文档问答助手。

【核心规则】你只能使用下方"检索到的文档信息"中的内容来回答问题。
- 绝对不要使用你自己的知识或训练数据来回答
- 如果检索到的文档中没有与问题相关的信息，你必须回答："根据现有文档库，未找到相关信息。请尝试换个问题表述，或咨询专业医疗人员。"
- 回答时必须引用来源文档的标题，格式：[来源: 文档标题]
- 使用专业但易懂的中文
- 不提供具体的医疗建议，只提供信息参考
- 如涉及严重疾病，请建议用户咨询专业医生

检索到的文档信息：
{context}

用户问题：{query}

请严格基于以上检索到的文档信息回答："""

VERIFICATION_PROMPT = """你是一个医疗回答质量验证专家。请验证以下回答是否完全忠实于参考资料。

【参考资料】
{context}

【用户问题】
{query}

【待验证的回答】
{response}

请从以下两个维度评估：
1. 忠实度：回答中的每个事实点是否都能在参考资料中找到依据？是否有"脑补"的内容？
2. 相关性：参考资料是否确实回答了用户的问题？

输出格式（严格遵循，只输出两行）：
VERDICT: PASS 或 FAIL
REASON: 简要说明原因（50字以内）"""


class RAGEngine:
    def __init__(self):
        self._initialized = False
        self._worker_script = os.path.join(os.path.dirname(__file__), "..", "..", "embedding_worker.py")
        self._worker_script = os.path.normpath(self._worker_script)

    async def _run_worker(self, args: list[str], timeout: int = 300) -> str:
        python_exe = sys.executable
        cmd = [python_exe, "-u", self._worker_script] + args
        env = os.environ.copy()

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)

        if proc.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="replace")
            raise RuntimeError(f"Worker failed (rc={proc.returncode}): {error_msg}")

        return stdout.decode("utf-8", errors="replace").strip()

    async def index_document(self, document: Document) -> int:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write(document.content)
            content_file = f.name

        try:
            result = await self._run_worker([
                "index",
                str(document.id),
                document.title,
                document.category,
                document.source or "",
                content_file
            ])
            data = json.loads(result)
            return data["chunk_count"]
        finally:
            os.unlink(content_file)

    async def delete_document(self, doc_id: int) -> None:
        await self._run_worker(["delete", str(doc_id)])

    async def _verify_response(self, query_text: str, context: str, response_text: str) -> dict:
        def _do_verify():
            from openai import OpenAI
            client = OpenAI(
                base_url=settings.ZHIPUAI_BASE_URL,
                api_key=settings.ZHIPUAI_API_KEY
            )
            prompt = VERIFICATION_PROMPT.format(
                context=context, query=query_text, response=response_text
            )
            result = client.chat.completions.create(
                model=settings.ZHIPUAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=200
            )
            return result.choices[0].message.content or ""
        try:
            verdict_text = await asyncio.to_thread(_do_verify)
            passed = "FAIL" not in verdict_text.upper()
            return {"passed": passed, "reason": verdict_text.strip()}
        except Exception as e:
            logger.warning("Verification failed: %s", e)
            return {"passed": True, "reason": f"验证服务暂不可用: {e}"}

    async def query(
        self,
        query_text: str,
        top_k: int = 5,
        retrieval_mode: str = "hybrid",
        db: Optional[AsyncSession] = None,
        user_id: Optional[int] = None
    ) -> dict:
        start_time = time.time()

        result_raw = await self._run_worker(["query", query_text, str(top_k), retrieval_mode])
        results = json.loads(result_raw)

        if not results.get("documents") or not results["documents"][0]:
            return {
                "response": "抱歉，未找到与您问题相关的医疗文档信息。请尝试重新表述您的问题，或咨询专业医疗人员。",
                "confidence": 0.0,
                "sources": [],
                "retrieval_mode": retrieval_mode,
                "verification": None,
                "processing_time": int((time.time() - start_time) * 1000)
            }

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]
        rrf_scores = results.get("rrf_scores", [None] * len(documents))

        context_parts = []
        sources = []
        seen_doc_ids = set()

        for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
            title = metadata.get("title", "未知")
            context_parts.append(f"[来源: {title}]\n{doc}")

            doc_id = metadata.get("doc_id")
            if doc_id and doc_id not in seen_doc_ids:
                seen_doc_ids.add(doc_id)
                relevance_score = max(0, 1 - distance)
                sources.append({
                    "id": doc_id,
                    "title": title,
                    "category": metadata.get("category", "unknown"),
                    "source": metadata.get("source", ""),
                    "content_preview": doc[:200] + "..." if len(doc) > 200 else doc,
                    "relevance_score": round(relevance_score, 4),
                    "rrf_score": rrf_scores[i] if i < len(rrf_scores) else None
                })

        context = "\n\n".join(context_parts)

        response_text = f"基于检索到的医疗文档，以下是相关信息：\n\n{context}\n\n（注：LLM服务暂不可用，以上为原始检索结果）"

        def _do_llm_call():
            from openai import OpenAI
            client = OpenAI(
                base_url=settings.ZHIPUAI_BASE_URL,
                api_key=settings.ZHIPUAI_API_KEY
            )
            prompt = MEDICAL_SYSTEM_PROMPT.format(context=context, query=query_text)
            response = client.chat.completions.create(
                model=settings.ZHIPUAI_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个专业的医疗AI助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=2048
            )
            return response.choices[0].message.content

        try:
            response_text = await asyncio.to_thread(_do_llm_call)
        except Exception as e:
            logger.warning("LLM call failed: %s", e)

        verification = await self._verify_response(query_text, context, response_text)
        if not verification["passed"]:
            logger.info("Verification FAILED: %s", verification['reason'])
            response_text = f"根据现有文档库，未能找到可靠信息来回答您的问题。\n\n验证说明：{verification['reason']}\n\n建议您尝试换个问题表述，或咨询专业医疗人员。"
            confidence = 0.0
        else:
            avg_score = sum(s["relevance_score"] for s in sources) / len(sources) if sources else 0
            confidence = min(avg_score * 100, 95)

        processing_time = int((time.time() - start_time) * 1000)

        log_id = 0
        if db and user_id:
            log = QueryLog(
                user_id=user_id,
                query=query_text,
                response=response_text,
                confidence=confidence,
                processing_time=processing_time,
                source_doc_ids=",".join(str(s["id"]) for s in sources),
                retrieval_mode=retrieval_mode
            )
            db.add(log)
            await db.commit()
            await db.refresh(log)
            log_id = log.id

        return {
            "id": log_id,
            "response": response_text,
            "confidence": confidence,
            "sources": sources,
            "retrieval_mode": retrieval_mode,
            "verification": verification,
            "processing_time": processing_time
        }


rag_engine = RAGEngine()
