import os
import sys

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

# 防止 Windows 控制台 GBK 编码打不出 emoji/特殊字符
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 加载环境变量 (项目根目录的 .env, 已加入 .gitignore, 不会被上传)
load_dotenv()

# 1、从环境变量中读取阿里云百炼的配置
base_url = os.getenv("DASHSCOPE_BASE_URL")
api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    raise RuntimeError("未读取到 DASHSCOPE_API_KEY, 请检查项目根目录 .env 文件")

# 2、初始化多模态模型 (qwen3.8-flash 支持图片输入)
model = init_chat_model(
    model="qwen3.8-flash",
    model_provider="openai",
    base_url=base_url,
    api_key=api_key,
)

# 3、创建Agent
agent = create_agent(model=model)

# 4、准备多模态消息: content 是一个列表, 由 文本块 + 图片块 组成
message = HumanMessage([
    {"type": "text", "text": "描述以下这张图片的内容！"},
    {"type": "image",
     "url": "https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg"},
])

# 5、流式调用 (注意状态键是 messages, 不是 message)
stream = agent.stream(
    input={"messages": [message]},
    stream_mode="messages",
)

for chunk, metadata in stream:
    if chunk.content:
        print(chunk.content, end="", flush=True)
print()
