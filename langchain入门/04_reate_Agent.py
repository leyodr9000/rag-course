import sys

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool

# 防止 Windows 控制台 GBK 编码打不出 emoji/特殊字符
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 加载环境变量 (项目根目录的 .env, 已加入 .gitignore, 不会被上传)
# langchain 会自动读取标准环境变量 OPENAI_API_KEY / OPENAI_BASE_URL,
# 代码里无需任何显式配置 (值见 .env 的 DeepSeek 官方段)
load_dotenv()

#定义工具
@tool
def getWeather(location: str) -> str:
    """查询指定城市的当前天气。location: 城市名或坐标"""
    return f"Current weather in {location} is Sunny!"

# create_agent有两个参数: 模型名称 tools表示工具
# (模型沿用本项目的 openai:deepseek-chat; 课件里的 deepseek-v4-pro 是中转站的贵模型)
agent = create_agent(
    model="openai:deepseek-chat",
    # 工具是列表，列表中是方法的名称，此处可以定义更多的方法
    tools=[getWeather]
)

# 4、调用Agent 智能体
print("正在调用大模型...")
response = agent.invoke({
    "messages": [
        {"role":"system","content":"你是一个热心的AI助手"},
        {"role":"user","content":"你好，我是巨哥"},
        {"role":"assistant","content":"你好，巨哥！很高兴认识你！！"},
        {"role":"user","content":"南阳今天天气怎么样？"}
    ]
})

# 5、打印响应结果
for message in response['messages']:
    print(message)
