import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv
from openai import OpenAI

# 防止 Windows 控制台 GBK 编码打不出 emoji/特殊字符
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 1. 加载 .env 文件 (在项目根目录, 已加入 .gitignore, 不会被上传)
#    本文件位于 项目根/01_AI通识与基础/ 下, 所以 parents[1] 就是项目根
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# 2. 从环境变量中读取 API_KEY
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise RuntimeError("未读取到 DEEPSEEK_API_KEY, 请检查项目根目录 .env 文件")

# 3. 创建 OpenAI 客户端 (DeepSeek 兼容 OpenAI 接口协议)
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
    timeout=60,
    # 不走系统代理 (与 01_OpenAI.py 同理, 避免本机 7890 代理干扰)
    http_client=httpx.Client(trust_env=False),
)

print("正在调用 DeepSeek......")
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": "你好,请用一句话介绍你自己"},
    ],
    stream=False,
    temperature=0.9,
)

print("模型回复:")
print(response.choices[0].message.content)
