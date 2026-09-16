import os
import sys

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

# 防止 Windows 控制台 GBK 编码打不出 emoji/特殊字符
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 加载环境变量 (项目根目录的 .env, 已加入 .gitignore, 不会被上传)
load_dotenv()

# 1、从环境变量中读取 DeepSeek 官方的配置
base_url = os.getenv("DEEPSEEK_BASE_URL")
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise RuntimeError("未读取到 DEEPSEEK_API_KEY, 请检查项目根目录 .env 文件")

# 2、初始化模型 (用最便宜的 deepseek-chat; "pro"/"reasoner" 系列更贵, 不用)
model = init_chat_model(
    model="deepseek-chat",       # DeepSeek 官方的模型名, 中转站那种 v4-flash 名字官方不认识
    model_provider="openai",     # 官方接口兼容 OpenAI 协议
    base_url=base_url,
    api_key=api_key,
)

# 方式一：invoke方法访问模型
# invoke函数是阻塞式调用，需要等待模型生成全部结果才会返回 --- 等待时间较长
# 简化写法的字符串会被LangChain默认是user的消息内容
response = model.invoke("你是谁呀？")
print("方式一(字符串):", response.content)

# 调用invoke方法，并且传入消息数组
response = model.invoke([
    {"role":"system","content":"你扮演火箭队的武藏，以武藏的性格口吻回答用户的问题"},
    {"role":"user","content":"你是谁呀？"}
])
print("方式二(消息数组):", response.content)

# 流式调用
stream = model.stream("你是谁呀？")
# stream 是一个生成器对象, 真正的内容要靠 for 循环逐块取
for chunk in stream:
    print(chunk.content, end="", flush=True)
print()
