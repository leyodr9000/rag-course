# 飞书文档任务总结报告（RAG 项目）

> 项目：基于RAG的QueryMind查询+智能项目（QueryMind 服装导购知识库问答系统）
> 执行：AI 编程助手（DeepSeek Harness + GLM）
> 日期：2026-09-14 ～ 2026-09-21
> 涵盖四次开发任务：《1. RAG 核心技术点：余弦相似度、文本嵌入与提示词模板》《2. 知识库更新服务开发（离线准备线）》《3. RAG 在线服务与多轮会话记忆》《4. Web 界面开发与工程化收尾》
> 说明：本篇与《星辰WMS 任务总结》对应，记录 AI 大模型方向（QueryMind）的开发过程；
> 所有实测数据均来自项目实际代码与真实运行结果（项目说明第 6 节），可直接引用。

---

## 任务一：《RAG 核心技术点》→ 四块基础能力

### 1.1 余弦相似度（纯 Python 实现）
- 手写点积、模长计算与除零校验，理解向量相似度的数学定义
- 再用 NumPy 批量计算并验证排序结果，确认与手写实现一致

### 1.2 文本嵌入（Text Embedding）
- 目标：把中文文本转为多维向量，语义相近的文本向量距离更近
- 踩坑：`OpenAIEmbeddings` 与百炼兼容接口不匹配，报 `Field required: input.contents`
- 解决：改用 DashScope 原生 SDK 调用 `text-embedding-v4`，再封装为 LangChain 可用的 Embeddings

### 1.3 提示词模板
- 掌握 `PromptTemplate`、`ChatPromptTemplate`、`FewShotChatMessagePromptTemplate`、`MessagesPlaceholder` 四件套
- 要点：模板本质是 Runnable 子类，可直接进入 LCEL 管道

### 1.4 LCEL 链路
- 用管道符 `|` 组合 提示词 → 模型 → 输出解析器
- 配合 `RunnableParallel`（并行分支）与 `RunnablePassthrough`（原样透传）
- 踩坑：普通 dict 没有 invoke 方法，链路中必须换成 Runnable 组件

### 1.5 文档加载器与文本切分器
- 加载器：`CSVLoader`、`JSONLoader`（jq 表达式中文键名需加引号）、`PyPDFLoader`、`TextLoader`
- 切分器：`RecursiveCharacterTextSplitter` 按自然边界递归切分（CHUNK_SIZE=1000、重叠 100、中英文混合分隔符）

---

## 任务二：《知识库更新服务开发》→ 离线准备线

### 2.1 上传页（Streamlit :8502）
- `st.file_uploader` 接收 TXT（accept_multiple_files=False）
- 踩坑：Streamlit 新版把 `filename` 改名为 `name`、`content_type` 改名为 `type`，`read()` 直接返回 bytes
- 页面用 `@st.cache_resource` 缓存服务实例，避免每次交互重建向量库

### 2.2 MD5 去重三件套
- `get_string_md5`：hashlib 计算文本指纹
- `check_md5`：逐行核对 md5.text 登记文件，已处理即跳过
- `save_md5`：追加模式登记新指纹
- 效果：同一文档重复上传返回“[跳过]内容已经存在知识库中!”，防止向量库重复膨胀

### 2.3 切分与入库
- 超过 MAX_SPLIT_CHAR_NUMBER（1000 字符）才执行切分，短文本整体成块
- Document 的 metadata 记录 source（来源文件名）——答案可溯源的基础
- 调用 text-embedding-v4 向量化，写入 Chroma（集合名 rag，持久化目录 chroma_db）

### 2.4 验证结果
- 3 个 TXT 文档 → 6 个文本块（尺码推荐 1 / 洗涤养护 3 / 颜色选择 2）全部入库
- md5.text 登记 3 条指纹；重复上传同一文档正确返回 [跳过]

---

## 任务三：《RAG 在线服务与多轮会话记忆》→ 在线服务线

### 3.1 会话记忆（文件落盘）
- 自定义 `FileChatMessageHistory` 继承 `BaseChatMessageHistory` 标准接口
- 实现 add_message / add_messages / messages / clear，以 session_id 为文件名 JSON 落盘
- 实测：写入 2 条消息 → 重建对象（模拟重启）→ 完整读回 2 条

### 3.2 提示词组装
- 结构：system(参考资料) + 历史消息（MessagesPlaceholder 注入）+ user(当前问题)
- 踩坑与修正：系统提示词曾把「知识库资料」和「对话历史」混为一谈，导致依赖历史的追问被拒答
  → 改为明确两个信息源：资料优先、历史次之、都没有才回答“未提及”

### 3.3 检索与生成
- 相似度检索取回命中文本块，合并为参考资料
- LCEL 链路流式生成，答案逐段返回前端

---

## 任务四：《Web 界面与工程化收尾》

### 4.1 双页设计
- 上传页：文件上传控件 + 入库结果展示（成功/跳过）
- 问答页：`st.chat_input` 提问 → `st.write_stream` 流式渲染 → 检索来源可展开

### 4.2 工程实践
- API 密钥存于 .env 并加入 .gitignore；chroma_db、chat_history、md5.text 等运行产物隔离不入库
- 检索结果带 source 元数据，答案可溯源
- Git 提交按功能拆分，整理项目说明文档归档

---

## 实测数据（真实运行记录）

| 项 | 结果 |
|---|---|
| 知识库 | 3 个 TXT → 6 个文本块全部入库 |
| 问答（资料命中） | “170cm/120斤” → L 码；“真丝连衣裙怎么洗” → 干洗/水温≤25℃/浸泡≤15分钟 |
| 追问改写 | “那羽绒服呢” → 改写为“羽绒服怎么洗”后命中洗涤养护，水温≤30℃ |
| 多轮记忆 | “我多高” → 从对话历史答出 180cm |
| 流式输出 | 单次回答 36 个片段实时渲染 |
| 记忆持久化 | 2 条写入 → 重建对象 → 完整读回 |

---

## 关键路径速查

| 内容 | 路径 |
|---|---|
| 项目根目录 | `C:\wyy\ai大模型开发\NYSF\NYSF\02_rag-course\RAG项目案例` |
| 虚拟环境 | `C:\wyy\ai大模型开发\NYSF\NYSF\.venv`（Python 3.14.6，uv 管理） |
| 向量库 | `RAG项目案例\chroma_db`（集合 rag，持久化） |
| 会话历史 | `RAG项目案例\chat_history\<session_id>.json` |
| MD5 登记 | `RAG项目案例\md5.text` |
| 测试语料 | `RAG项目案例\data\`（尺码推荐/洗涤养护/颜色选择 TXT × 3） |
| 问答页 | `http://localhost:8501`（app_qa.py） |
| 上传页 | `http://localhost:8502`（app_file_uploader.py） |

---

## 遗留 / 建议

1. **CHUNK_SIZE=1000 粒度偏大**：单文件仅切 1-3 块，检索精度受限 → 建议调至 300、重叠 50
2. **语料规模小**：仅 3 文档 6 块，Top-K 会带入无关内容 → 语料扩充后自然缓解，也可加相似度阈值过滤
3. **仅支持 TXT**：扩展 PDF / Word / Markdown（前置课件已覆盖 PyPDFLoader 等加载器）
4. **查询改写增加一次模型调用**：可加规则判断，仅对明显的短追问触发改写
5. **密钥安全**：所有 key 走 .env（已 gitignore）；若曾把 key 粘贴到聊天/文档，建议定期轮换
