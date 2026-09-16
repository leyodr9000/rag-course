import os
import sys

import httpx
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 防止 Windows 控制台 GBK 编码打不出 emoji/特殊字符
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 加载环境变量 (项目根目录的 .env, 已加入 .gitignore, 不会被上传)
load_dotenv()

# 1. 从环境变量中读取 API_KEY (放在最前面, 创建模型和 Agent 都要用)
api_key = os.getenv("TOKENRHYTHM_API_KEY")
if not api_key:
    raise RuntimeError("未读取到 TOKENRHYTHM_API_KEY, 请检查项目根目录 .env 文件")

#2.定义工具
from langchain.tools import tool

@tool
def getWeather(location: str) -> str:
    """查询指定城市的当前天气。location: 城市名或坐标"""
    return f"Current weather in {location} is Sunny!"

#3.创建Agent
# 新版 langchain 的 create_agent 不接收 base_url 参数,
# 改为传入 ChatOpenAI 实例, 由它指定中转站地址、密钥和模型
from langchain.agents import create_agent

llm = ChatOpenAI(
    model="deepseek-v4-flash-0731",
    api_key=api_key,
    base_url="https://tokenrhythm.studio/v1",
    timeout=60,
    # 不走系统代理: 本机 127.0.0.1:7890 代理对该站点 TLS 握手异常, 直连正常
    http_client=httpx.Client(trust_env=False),
)

agent = create_agent(
    llm,
    tools=[getWeather],
)

#4.调用Agent智能体
print("正在调用大模型......")
result = agent.invoke(
    {
        "messages": [
            {"role": "user", "content": "陕西西安今天的天气如何？"}
        ]
    }
)

print("Agent 最终回复:")
print(result["messages"][-1].content)
