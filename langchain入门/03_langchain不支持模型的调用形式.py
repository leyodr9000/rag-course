import os
import sys

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

# 防止 Windows 控制台 GBK 编码打不出 emoji/特殊字符
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 加载环境变量 (项目根目录的 .env, 已加入 .gitignore, 不会被上传)
load_dotenv()

# 1、从环境变量中读取阿里云百炼的配置
base_url = os.getenv("DASHSCOPE_BASE_URL")
api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    raise RuntimeError("未读取到 DASHSCOPE_API_KEY, 请在项目根目录 .env 中填入阿里云百炼的 API-KEY")

# 2、初始化模型 (langchain 不直接支持的模型 → 通过兼容 OpenAI 协议的形式调用)
model = init_chat_model(
    model="qwen3.8-flash",       # 模型名称，这里可以自定义
    model_provider="openai",     # 阿里云百炼兼容 OpenAI 协议，指定 openai 提供商
    base_url=base_url,
    api_key=api_key,
)

print(model)

# 3、在 .env 里填好 DASHSCOPE_API_KEY 后, 可以取消下面注释试一次真实调用
# print("正在调用大模型......")
# response = model.invoke("你好，请用一句话介绍你自己")
# print(response.content)
