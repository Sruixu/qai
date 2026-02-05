# QAI (Quality AI) 智能测试平台

QAI 是一款基于 RAG (检索增强生成) 技术的下一代智能测试用例管理平台。它不仅是一个传统的用例管理工具，更是一个能“听懂”需求、自动生成高质量测试用例的 AI 助手。通过集成 DeepSeek、Kimi、MiniMax 等国产大模型，QAI 致力于将测试人员从繁琐的编写工作中解放出来。

## ✨ 核心功能

*   **🤖 多模型 AI 驱动**:
    *   全面支持 **DeepSeek (V3/R1)**、**Kimi (Moonshot)**、**MiniMax**、**Qwen**、**Gemini**、**OpenAI** 等主流大模型。
    *   内置“智能向导”，支持 **模块拆分 -> 场景设计 -> 用例生成** 的 3 阶段人机协同工作流。
*   **📚 RAG 知识库增强**:
    *   自动将历史用例沉淀为向量知识库。
    *   AI 生成新用例时，会自动参考历史相似用例的边界值和测试技巧，越用越聪明。
*   **⚡ 自动化脚本转换**:
    *   支持将自然语言描述的测试步骤，一键转换为 **Python Playwright** 自动化测试代码。
*   **📊 数据无缝流转**:
    *   支持 **Excel (.xlsx)** 和 **CSV** 格式的双向导入导出。
    *   智能识别表头，无需复杂配置即可迁移历史数据。
*   **🎯 灵活管理**:
    *   支持需求/用例的增删改查、优先级筛选、多维度搜索。

## 🚀 快速开始

### 1. 环境准备
确保您的环境中已安装 Python 3.8+。

### 2. 后端启动
```bash
cd qai/backend
pip install -r requirements.txt
# 核心依赖: fastapi, uvicorn, sqlmodel, langchain, chromadb, pandas, openpyxl
uvicorn main:app --reload --port 8000
```

### 3. 前端启动
前端为纯静态 Vue3 单页应用，直接通过 HTTP 服务器运行即可。
```bash
cd qai/frontend
python -m http.server 8080
```

### 4. 访问系统
打开浏览器访问: `http://localhost:8080`

## 🛠️ 技术栈

*   **Frontend**: Vue 3 (Composition API), Element Plus
*   **Backend**: FastAPI, SQLModel (SQLite)
*   **AI & RAG**: LangChain, ChromaDB (Vector Store)
*   **Data Processing**: Pandas, OpenPyXL

## 📝 许可证
MIT License
