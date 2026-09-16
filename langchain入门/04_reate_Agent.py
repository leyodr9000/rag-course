import sys

from dotenv import load_dotenv
from langchain.agents import create_agent

# 防止 Windows 控制台 GBK 编码打不出 emoji/特殊字符
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 加载环境变量 (项目根目录的 .env, 已加入 .gitignore, 不会被上传)
# langchain 会自动读取标准环境变量 OPENAI_API_KEY / OPENAI_BASE_URL,
# 代码里无需任何显式配置 (值见 .env 的 DeepSeek 官方段)
load_dotenv()

agent = create_agent(model="openai:deepseek-chat")

# response = agent.invoke({
#     "messages":[{"role":"user","content":"你是谁呀？"}]
# })
# print(response)

# stream_mode 表示流的模式，也是智能体中特有的方式
messages = agent.stream(
    input={
        "messages": [{"role": "user", "content": "你是谁呀？"}]
    },
    stream_mode="messages",
)

print(type(messages))
for token, metadata in messages:
    if token.content:
        print(token.content, end="", flush=True)
print()
