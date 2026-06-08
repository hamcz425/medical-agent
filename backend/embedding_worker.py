import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

import json
import pickle
import chromadb
import jieba
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
COLLECTION_NAME = "medical_documents"
BM25_INDEX_PATH = os.path.join(CHROMA_DIR, "bm25_index.pkl")


def chunk_text(text, max_length=512, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_length
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    return chunks


def save_bm25_index(bm25, chunk_ids, chunk_texts, chunk_metadatas):
    os.makedirs(CHROMA_DIR, exist_ok=True)
    with open(BM25_INDEX_PATH, "wb") as f:
        pickle.dump({
            "bm25": bm25,
            "ids": chunk_ids,
            "texts": chunk_texts,
            "metadatas": chunk_metadatas
        }, f)


def load_bm25_index():
    if not os.path.exists(BM25_INDEX_PATH):
        return None
    with open(BM25_INDEX_PATH, "rb") as f:
        return pickle.load(f)


def rebuild_bm25_from_chromadb():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )
    if collection.count() == 0:
        return None

    all_data = collection.get(include=["documents", "metadatas"])
    if not all_data["ids"]:
        return None

    tokenized_corpus = [list(jieba.cut(doc)) for doc in all_data["documents"]]
    bm25 = BM25Okapi(tokenized_corpus)
    save_bm25_index(bm25, all_data["ids"], all_data["documents"], all_data["metadatas"])
    return bm25


def index_document(doc_id, title, content, category, source):
    model = SentenceTransformer(MODEL_NAME)

    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    chunks = chunk_text(content)
    embeddings = model.encode(chunks, normalize_embeddings=True, show_progress_bar=False).tolist()

    ids = [f"doc_{doc_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "doc_id": doc_id,
            "title": title,
            "category": category,
            "source": source or "",
            "chunk_index": i
        }
        for i in range(len(chunks))
    ]

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas
    )

    rebuild_bm25_from_chromadb()

    return len(chunks)


def vector_search(query_text, top_k, model, collection):
    query_embedding = model.encode([query_text], normalize_embeddings=True).tolist()[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    if not results["ids"][0]:
        return []
    items = []
    for i in range(len(results["ids"][0])):
        items.append({
            "id": results["ids"][0][i],
            "document": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
            "vector_rank": i + 1
        })
    return items


def bm25_search(query_text, top_k, bm25_data):
    if bm25_data is None:
        return []
    query_tokens = list(jieba.cut(query_text))
    bm25_scores = bm25_data["bm25"].get_scores(query_tokens)
    ranked_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:top_k]
    items = []
    for rank, idx in enumerate(ranked_indices):
        items.append({
            "id": bm25_data["ids"][idx],
            "document": bm25_data["texts"][idx],
            "metadata": bm25_data["metadatas"][idx],
            "bm25_score": float(bm25_scores[idx]),
            "bm25_rank": rank + 1
        })
    return items


def reciprocal_rank_fusion(vector_results, bm25_results, k=60):
    scores = {}
    doc_data = {}

    for rank, item in enumerate(vector_results):
        doc_id = item["id"]
        scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank + 1)
        doc_data[doc_id] = item

    for rank, item in enumerate(bm25_results):
        doc_id = item["id"]
        scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank + 1)
        if doc_id not in doc_data:
            doc_data[doc_id] = item

    ranked_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    results = []
    for doc_id in ranked_ids:
        item = doc_data[doc_id].copy()
        item["rrf_score"] = round(scores[doc_id], 6)
        results.append(item)
    return results


def query_documents(query_text, top_k=5, mode="hybrid"):
    model = SentenceTransformer(MODEL_NAME)

    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    search_k = top_k * 3 if mode == "hybrid" else top_k

    if mode == "bm25":
        bm25_data = load_bm25_index()
        if bm25_data is None:
            bm25_data = rebuild_bm25_from_chromadb()
        if bm25_data is None:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
        bm25_results = bm25_search(query_text, top_k, bm25_data)
        results = bm25_results[:top_k]
    elif mode == "vector":
        results = vector_search(query_text, top_k, model, collection)
    else:
        bm25_data = load_bm25_index()
        if bm25_data is None:
            bm25_data = rebuild_bm25_from_chromadb()
        vector_results = vector_search(query_text, search_k, model, collection)
        bm25_results = bm25_search(query_text, search_k, bm25_data) if bm25_data else []
        results = reciprocal_rank_fusion(vector_results, bm25_results)[:top_k]

    if not results:
        return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    return {
        "documents": [[r["document"] for r in results]],
        "metadatas": [[r["metadata"] for r in results]],
        "distances": [[r.get("distance", 0) for r in results]],
        "rrf_scores": [r.get("rrf_score") for r in results]
    }


def delete_document(doc_id):
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    try:
        collection.delete(where={"doc_id": doc_id})
    except Exception:
        pass

    rebuild_bm25_from_chromadb()
    return True


if __name__ == "__main__":
    action = sys.argv[1]

    if action == "index":
        doc_id = int(sys.argv[2])
        title = sys.argv[3]
        category = sys.argv[4]
        source = sys.argv[5]
        content_file = sys.argv[6]

        with open(content_file, "r", encoding="utf-8") as f:
            content = f.read()

        chunk_count = index_document(doc_id, title, content, category, source)
        print(json.dumps({"ok": True, "chunk_count": chunk_count}))

    elif action == "query":
        query_text = sys.argv[2]
        top_k = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        mode = sys.argv[4] if len(sys.argv) > 4 else "hybrid"
        results = query_documents(query_text, top_k, mode)
        print(json.dumps(results, ensure_ascii=False))

    elif action == "delete":
        doc_id = int(sys.argv[2])
        delete_document(doc_id)
        print(json.dumps({"ok": True}))
