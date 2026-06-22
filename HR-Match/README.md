# HR-Match — 多Agent简历智能匹配系统

基于 **FastAPI + Vue 3** 的多 Agent 协作简历-岗位匹配系统，HR 输入自然语言 JD 即可自动分析简历、输出排名和面试建议。

## 功能

- **自然语言 JD**：HR 用人话写岗位要求，系统自动结构化
- **2 Agent 协作**：Resume Agent 提取简历信息，Match Agent 评分匹配
- **可调权重 + 偏好**：技能/学历/经验滑块 + 自然语言筛选偏好
- **能力评估**：项目深度、技能自洽性、成长潜力、亮点多维度评价
- **双格式支持**：PDF/Word 统一提取，支持表格内容和批量文件夹导入
- **详细报告**：计算过程、维度评分、不足分析、面试建议

## 实现

### Agent 设计

| Agent | 职责 |
|-------|------|
| Resume Agent | 提取姓名/技能/学历/经验/项目/证书，标记量化数据 |
| Match Agent | 硬规则评分（技能映射表）+ LLM 语义理解，输出能力评估 |

Agent 通过结构化 JSON 通信，不依赖任何框架（LangChain/CrewAI/AutoGen），纯原生 OpenAI SDK。

### 评分规则

- 技能：同名 100%，同类可迁移 70%（Flask↔Django），不同方向 0%
- 学历：同级 100 / 高一级 110 / 低一级上限 70
- 经验：按比例折算，下限 50
- 能力评估：不影响总分，独立输出项目深度/自洽性/潜力/亮点
- 所有维度附计算依据，评分透明可追溯

### 文档提取

PyMuPDF + python-docx 统一管道，支持单页/多页 PDF、标准段落和表格布局 Word，结构异常时自动降级不崩溃。

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | FastAPI + SQLAlchemy + SQLite |
| 前端 | Vue 3 + Vite |
| Agent | 原生 OpenAI SDK |
| LLM | DeepSeek-chat |
| 文档解析 | PyMuPDF + python-docx |
| 搜索 | Tavily API |

## 快速开始

```bash
# 后端
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --port 8000

# 前端
cd frontend
npm install
npm run dev
```

打开 `http://localhost:3000`，输入 `deepseek.env` 配置 API Key。

## 项目结构

```
backend/
├── main.py / config.py / database.py / models.py / schemas.py
├── llm_client.py / extractor.py / prompts.py
└── agent/
    ├── resume_agent.py / match_agent.py / coordinator.py
frontend/
└── src/App.vue / router/ / views/JobListPage.vue / JobDetailPage.vue
```
