# 医疗RAG智能问答系统 (Medical RAG Agent)

企业级医疗知识问答系统，基于检索增强生成(RAG)技术，提供精准的医疗信息检索和智能问答能力。支持BM25关键词检索、向量语义检索、混合检索三种模式，配备Self-RAG验证机制确保回答质量。

## 技术栈

### 后端
- **框架**: FastAPI (Python 3.13)
- **数据库**: SQLAlchemy + SQLite (可切换PostgreSQL)
- **向量库**: ChromaDB (本地持久化)
- **关键词检索**: BM25 (rank_bm25 + jieba分词)
- **检索融合**: Reciprocal Rank Fusion (RRF)
- **LLM**: 智谱 GLM-4-Flash (OpenAI兼容接口，国内免费)
- **Embedding**: paraphrase-multilingual-MiniLM-L12-v2 (本地运行，384维)
- **认证**: JWT + RBAC (admin/doctor/viewer)

### 前端
- **框架**: React 18 + TypeScript
- **UI组件**: Ant Design 5
- **构建工具**: Webpack 5 (自定义配置)
- **HTTP客户端**: Axios

## 核心功能

1. **RAG智能问答** - 基于医疗知识库的精准问答，支持三种检索模式
2. **混合搜索** - BM25关键词 + 向量语义，RRF融合排序 (k=60)
3. **Self-RAG验证** - 第二次LLM调用验证回答忠实度，不可靠回答自动拒绝
4. **置信度评估** - 基于文档相关性评分的AI回答可信度
5. **引用追溯** - 每个回答标注来源文档
6. **医生反馈(HITL)** - 人工在环：正确/有误/部分正确反馈机制
7. **文档管理** - 医疗文档的增删改查、分类管理、文件上传(txt/md/pdf/docx)
8. **JWT认证** - 多角色权限控制 (admin/doctor/viewer)
9. **查询历史** - 分页浏览历史查询，保留检索模式标签
10. **系统监控** - 实时统计和健康状态

## 架构设计

```
用户查询
   │
   ▼
┌─────────────────────┐
│   检索模式选择       │  hybrid / vector / bm25
└─────────┬───────────┘
          │
    ┌─────┴─────┐
    ▼           ▼
┌────────┐ ┌────────┐
│ BM25   │ │ 向量   │  并行检索
│ 关键词  │ │ 语义   │
└───┬────┘ └───┬────┘
    │          │
    ▼          ▼
┌─────────────────────┐
│  RRF 融合排序(k=60) │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  LLM 生成回答        │  智谱 GLM-4-Flash
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Self-RAG 验证       │  第二次LLM调用
│  忠实度 + 相关性     │
└─────────┬───────────┘
          │
     PASS │ FAIL
          ▼
┌─────────────────────┐ 返回可靠回答 / 安全拒绝
└─────────────────────┘
```

## 成本优势

| 项目 | 本方案 | OpenAI方案 |
|------|--------|-----------|
| LLM | **¥0** (智谱GLM-4-Flash，国内免费无限额) | $2.50-10/百万token |
| Embedding | **¥0** (本地MiniLM-L12-v2) | $0.02/百万token |
| 向量库 | **¥0** (ChromaDB本地) | $0 |
| **月总计** | **¥0** | ~$780 |

## 项目结构

```
medical-agent/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI入口，CORS，路由注册
│   │   ├── config.py            # 配置管理 (环境变量)
│   │   ├── database.py          # SQLAlchemy异步数据库连接
│   │   ├── models/
│   │   │   ├── user.py          # 用户模型
│   │   │   ├── document.py      # 文档模型
│   │   │   └── query_log.py     # 查询日志 (含反馈字段)
│   │   ├── schemas/             # Pydantic请求/响应模型
│   │   ├── routers/
│   │   │   ├── auth.py          # 登录/注册/用户信息
│   │   │   ├── documents.py     # 文档CRUD + 上传 + 索引
│   │   │   ├── rag.py           # RAG查询 + 反馈 + 历史 + 统计
│   │   │   └── system.py        # 健康检查 + 指标
│   │   ├── services/
│   │   │   ├── rag_engine.py    # RAG核心：检索→生成→验证
│   │   │   ├── embedding_service.py  # 子进程Embedding (解决Win+Py3.13兼容)
│   │   │   ├── document_service.py   # 文档业务逻辑
│   │   │   └── auth_service.py       # JWT认证 + RBAC
│   │   └── utils/
│   │       └── auth.py          # 密码哈希 + Token工具
│   ├── embedding_worker.py      # ChromaDB + BM25 子进程 (独立Python进程)
│   ├── seed_documents.py        # 种子数据：创建用户 + 8篇医疗文档 + 索引
│   ├── requirements.txt
│   └── .env                     # 环境变量 (需自行配置)
├── frontend/
│   ├── src/
│   │   ├── index.tsx            # React入口
│   │   ├── App.tsx              # 路由 + 认证守卫 + 404
│   │   ├── types.ts             # TypeScript类型定义
│   │   ├── api/index.ts         # Axios封装 + API接口
│   │   ├── pages/
│   │   │   ├── Login.tsx        # 登录/注册
│   │   │   ├── Dashboard.tsx    # 数据概览
│   │   │   ├── Documents.tsx    # 文档管理
│   │   │   ├── RAGQuery.tsx     # RAG查询 + 历史 + 反馈
│   │   │   └── Settings.tsx     # 系统设置 (localStorage)
│   │   └── components/
│   │       └── Header.tsx       # 导航栏
│   ├── webpack.config.js        # 自定义Webpack配置
│   ├── tsconfig.json
│   └── package.json
├── docker-compose.yml
└── README.md
```

## 快速开始

### 环境要求
- Python 3.13+
- Node.js 18+
- npm

### 1. 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 配置环境变量 (复制并编辑)
copy .env.example .env
# 必须设置: ZHIPUAI_API_KEY=你的智谱API密钥
# 智谱API密钥申请: https://open.bigmodel.cn/

# 启动服务
python run.py
# 后端运行在 http://localhost:8000
```

### 2. 初始化数据

```bash
# 在backend目录下，确保后端已启动
python seed_documents.py
# 自动创建: 医生账号 + 8篇医疗文档 + 全部索引
```

### 3. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npx webpack serve --mode development --port 3001
# 前端运行在 http://localhost:3001
```

### 4. 登录系统

- 打开 http://localhost:3001
- 账号: `doctor1` / 密码: `doctor123`
- 选择RAG查询页面，输入医疗问题测试

### 5. Docker部署 (可选)

```bash
docker-compose up -d
# 前端: http://localhost:3001
# 后端: http://localhost:8000
# API文档: http://localhost:8000/docs
```

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| ZHIPUAI_API_KEY | 智谱AI API密钥 (必填) | - |
| ZHIPUAI_BASE_URL | 智谱API地址 | https://open.bigmodel.cn/api/paas/v4/ |
| ZHIPUAI_MODEL | LLM模型 | glm-4-flash |
| SECRET_KEY | JWT密钥 | change-me-in-production |
| DATABASE_URL | 数据库连接 | sqlite+aiosqlite:///./medical_agent.db |
| CHROMA_PERSIST_DIR | ChromaDB存储路径 | ./chroma_db |

## 角色权限

| 操作 | 查看者 (viewer) | 医生 (doctor) | 管理员 (admin) |
|------|:---:|:---:|:---:|
| RAG查询 | ✅ | ✅ | ✅ |
| 查看文档/历史 | ✅ | ✅ | ✅ |
| 创建/上传文档 | ❌ | ✅ | ✅ |
| 编辑文档 | ❌ | ✅ | ✅ |
| 索引文档 | ❌ | ✅ | ✅ |
| 删除文档 | ❌ | ❌ | ✅ |

## 亮点

1. **零成本架构** - 智谱GLM-4-Flash(免费无限额) + 本地Embedding(¥0)
2. **混合检索 + RRF融合** - BM25关键词 + 向量语义双路检索，Reciprocal Rank Fusion融合排序
3. **Self-RAG验证机制** - 生成后二次LLM验证忠实度，不可靠回答自动拒绝，提升可信度
4. **子进程Embedding架构** - 解决Windows+Python3.13下SentenceTransformer死锁问题
5. **医生反馈(HITL)** - 人工在环反馈机制，支持正确/有误/部分正确标注
6. **RBAC权限控制** - admin/doctor/viewer三级角色，接口级权限拦截
7. **完整工程实践** - JWT认证、异步API、数据库迁移、Docker部署

## License

MIT
