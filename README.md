# QAI (Quality AI) 智能测试平台

QAI 是一款基于 RAG (检索增强生成) 技术的下一代智能测试用例管理平台。它不仅是一个传统的用例管理工具，更是一个能“听懂”需求、自动生成高质量测试用例的 AI 助手。通过集成 DeepSeek、Kimi、MiniMax 等国产大模型，QAI 致力于将测试人员从繁琐的编写工作中解放出来。

## ✨ 核心功能

*   **🤖 多模型 AI 驱动**:
    *   全面支持 **DeepSeek (V3/R1)**、**Kimi (Moonshot)**、**MiniMax**、**Qwen**、**Gemini**、**OpenAI** 等主流大模型。
    *   内置“智能向导”，支持 **模块拆分 -> 场景设计 -> 用例生成** 的 3 阶段人机协同工作流。
*   **📚 RAG 知识库增强**:
    *   自动将历史用例沉淀为向量知识库。
    *   AI 生成新用例时，会自动参考历史相似用例的边界值和测试技巧，越用越聪明。
    *   **知识库去重**: 智能检测重复的知识条目，避免冗余。
*   **⚡ 自动化脚本转换**:
    *   支持将自然语言描述的测试步骤，一键转换为 **Python Playwright** 自动化测试代码。
*   **📊 数据无缝流转**:
    *   支持 **Excel (.xlsx)** 和 **CSV** 格式的双向导入导出。
    *   智能识别表头，无需复杂配置即可迁移历史数据。
*   **🎯 灵活管理**:
    *   支持需求/用例的增删改查、优先级筛选、多维度搜索。
    *   **项目版本管理**: 支持多项目、多版本管理，方便迭代回溯。
    *   **批量操作**: 支持用例批量删除，提高维护效率。

## 🚀 快速开始

### 方式一：一键启动 (Windows)

项目根目录下提供了便捷的启动脚本，只需双击运行即可。

1. 双击 `start.bat`。
2. 脚本会自动检查 Python 环境并安装依赖。
3. 启动成功后，控制台会显示访问地址。
   - 本机访问: `http://localhost:8080`
   - 局域网访问: 脚本会自动显示本机 IP，例如 `http://192.168.1.X:8000`

### 方式二：手动启动

#### 1. 环境准备
确保您的环境中已安装 Python 3.10+。

#### 2. 启动后端
```bash
cd backend
pip install -r requirements.txt
# 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### 3. 访问前端
本项目前端已集成到后端静态文件服务中，后端启动后，直接访问后端地址即可：
`http://localhost:8000`

## 📂 项目结构

```
qai/
├── backend/                # 后端代码 (FastAPI)
│   ├── app/
│   │   ├── core/           # 核心配置 (DB, Vector Store)
│   │   ├── models/         # 数据模型 (SQLModel)
│   │   ├── routers/        # API 路由
│   │   └── services/       # 业务逻辑 (LLM, RAG)
│   ├── chroma_db/          # 向量数据库存储
│   ├── database.db         # SQLite 数据库
│   ├── main.py             # 入口文件
│   └── requirements.txt    # 依赖列表
├── frontend/               # 前端代码
│   └── index.html          # Vue3 单页应用入口
├── start.bat               # Windows 一键启动脚本
├── README.md               # 项目说明文档
└── .gitignore              # Git 忽略配置
```

## 🛠️ 技术栈

*   **Frontend**: Vue 3 (Composition API), Element Plus, Axios
*   **Backend**: FastAPI, SQLModel (SQLite)
*   **AI & RAG**: LangChain, ChromaDB (Vector Store), OpenAI API Compatible
*   **Data Processing**: Pandas, OpenPyXL

## 📝 许可证
MIT License
