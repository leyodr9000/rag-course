# rag-course · AI 大模型课程实训项目

从调用大模型 API 的第一行代码，到基于 **RAG（检索增强生成）** 的知识库问答系统 **QueryMind**——
本项目完整记录了 AI 大模型应用开发的学习路径：基础调用 → 流式输出 → 多轮记忆 → 工具调用 → 多模态 → RAG 工程。

> 亮点：命令行聊天机器人（多轮+上下文+exit 退出）｜少样本文本分类｜多模态图片理解｜
> QueryMind：文档上传 → 切分入库 → 向量检索 → 流式问答（Streamlit 双页）

## 📁 目录结构

```
rag-course/
├── 01_AI通识与基础/                        # OpenAI SDK 基础
│   ├── 01_OpenAI.py                        # 基础调用（人设 + 完整响应对象）
│   ├── 02_OpenAI库的流式输出.py            # stream=True 逐块输出
│   ├── 03_OpenAI库附带历史消息调用模型.py  # 消息数组 / 多轮上下文
│   ├── 04_金融文本分类.py                  # 少样本（few-shot）文本分类
│   ├── 05_JSON的使用.py                    # （占位）
│   ├── 06_金融信息抽取.py                  # 结构化信息抽取（JSON 输出）
│   └── 07_命令行聊天机器人.py              # ⭐ 多轮对话 + exit 退出的聊天机器人
├── langchain入门/
│   ├── 01_langchain入门.py                 # create_agent 智能体入门
│   ├── 02_Models模型.py                    # init_chat_model + invoke/stream
│   ├── 03_langchain不支持模型的调用形式.py # 兼容 OpenAI 协议接入第三方模型
│   ├── 04_reate_Agent.py                   # Agent + @tool 工具 + 历史消息 + 消息类型分类
│   └── 06_多模态模型.py                    # 图片理解（HumanMessage 多模态块）
├── RAG项目案例/                            # ⭐ QueryMind 知识库问答系统
│   ├── config_data.py                      # 统一配置（路径/参数/模型名）
│   ├── knowledge_base.py                   # 知识库：MD5 去重 + 切分 + 入库
│   ├── vector_stores.py                    # 向量存储服务 + 检索器
│   ├── rag.py                              # RAG 核心链路（LCEL + 历史增强）
│   ├── file_history_store.py               # 文件会话记忆（JSON 落盘）
│   ├── app_file_uploader.py                # 上传页（Streamlit :8502）
│   ├── app_qa.py                           # 问答页（Streamlit :8501）
│   └── data/                               # 测试语料（服装领域 TXT × 3）
├── 实训报告-李少龙-25.33.docx              # 课程实训报告
└── src/rag_course/                         # 包骨架
```

## 🧰 技术栈（实测版本）

| 类别 | 组件 | 版本 |
|---|---|---|
| 语言 / 环境 | Python 3.12 + uv | 3.12.13 |
| 应用框架 | langchain / langchain-core | 1.4.0 / 1.6.3 |
| | langchain-openai / langchain-community | 1.6.2 / 0.4.2 |
| | langgraph（create_agent 底层） | 1.2.11 |
| 向量库 | langchain-chroma / chromadb | 1.1.0 / 1.5.9 |
| 模型服务 | 阿里云百炼（qwen3.8-flash 对话 + text-embedding-v4 嵌入） | dashscope 1.27.6 |
| | DeepSeek 官方（deepseek-chat） | openai 3.14.1 |
| Web 界面 | streamlit | 1.64.0 |
| 配置 | python-dotenv（.env） | 1.0.1 |

## 🚀 快速开始

```bash
# 1. 克隆
git clone https://github.com/leyodr9000/rag-course.git
cd rag-course

# 2. 安装依赖（需要 Python 3.12+，推荐 uv）
uv sync

# 3. 配置密钥：在项目根目录创建 .env，按需填入（模板如下，用哪家填哪家）
```

`.env` 模板（**切勿提交到仓库**）：

```ini
# DeepSeek 官方
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 阿里云百炼（对话 + 嵌入）
DASHSCOPE_API_KEY=
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# OpenAI 兼容中转站（可选）
TOKENRHYTHM_API_KEY=
TOKENRHYTHM_BASE_URL=https://tokenrhythm.studio/v1
```

## 🤖 运行 QueryMind 知识库问答系统

```bash
cd RAG项目案例

# 知识库上传页（浏览器打开 http://localhost:8502）
uv run streamlit run app_file_uploader.py --server.port 8502

# 问答页（浏览器打开 http://localhost:8501）
uv run streamlit run app_qa.py --server.port 8501

# 命令行验证 RAG 链路
uv run python rag.py
```

> 首次提问会初始化检索器与模型连接，稍慢属正常现象。

## 📚 课程练习运行方式

各练习均可独立运行（部分需先在 `.env` 配好对应变量）：

```bash
uv run python "01_AI通识与基础/07_命令行聊天机器人.py"   # 多轮对话机器人，exit 退出
uv run python "langchain入门/02_Models模型.py"           # init_chat_model + invoke/stream
uv run python "langchain入门/06_多模态模型.py"           # 图片理解（qwen3.8-flash 视觉）
```

## 🔍 QueryMind 工作原理

```
【离线准备线】上传 TXT → MD5 指纹去重 → RecursiveCharacterTextSplitter 切分(1000/100)
            → text-embedding-v4 向量化 → 存入 Chroma（持久化 chroma_db）

【在线服务线】用户提问 → (可选)历史注入 → 向量相似度检索 top-k
            → 命中文本块合并为参考资料 → system(资料) + 历史 + 问题 组装提示词
            → 大模型流式生成 → st.write_stream 实时渲染 → 写回会话历史
```

核心设计：**MD5 去重**防止重复入库膨胀；**Chroma 持久化**保证重启后可检索；
**RunnableWithMessageHistory** 让任意链路获得多轮记忆；**答案可溯源**（检索结果带 source 元数据）。

## 📊 实测结果

- 知识库：3 个 TXT 文档 → 6 个文本块全部入库，`md5.text` 登记 3 条指纹
- 重复上传同一文档：正确返回“[跳过]内容已经存在知识库中!”
- 知识库问答：“体重 180 斤尺码推荐” → 结合资料分身高档位回答（3XL/4XL）
- 提示词约束：“针织毛衣如何保养”（资料未覆盖）→ 模型如实说明并只给通用建议，不编造条目
- 多轮会话：24 条消息 JSON 落盘，模拟重启后完整读回
- 流式输出：单次回答 36 个片段实时渲染

## ⚠️ 已知不足与 Roadmap

- [ ] `CHUNK_SIZE=1000` 粒度偏大 → 计划调整为 300/重叠 50，提升检索精度
- [ ] 仅支持 TXT 上传 → 扩展 PDF / Word / Markdown（PyPDFLoader 等前置课件已覆盖）
- [ ] 检索仅返回 1 条 → 增大 k 并叠加相似度阈值过滤
- [ ] 短追问（省略主语）召回待加强 → 查询改写环节
- [ ] `05_JSON的使用.py` 占位待补

## 🔒 安全说明

- 所有 API 密钥仅存于 `.env`（已被 `.gitignore` 忽略），仓库内无任何密钥
- `chroma_db/`、`chat_history/`、`md5.text` 等运行产物同样不入库
