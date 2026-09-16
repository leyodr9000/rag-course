import os
import sys

import httpx
from dotenv import load_dotenv
from openai import OpenAI

# 防止 Windows 控制台 GBK 编码打不出 emoji/特殊字符
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 加载环境变量 (项目根目录的 .env, 已加入 .gitignore, 不会被上传)
load_dotenv()

# 从环境变量中读取 API_KEY
api_key = os.getenv("TOKENRHYTHM_API_KEY")
if not api_key:
    raise RuntimeError("未读取到 TOKENRHYTHM_API_KEY, 请检查项目根目录 .env 文件")

client = OpenAI(
    api_key=api_key,
    base_url="https://tokenrhythm.studio/v1",
    timeout=60,
    # 不走系统代理: 本机 127.0.0.1:7890 代理对该站点 TLS 握手异常, 直连正常
    http_client=httpx.Client(trust_env=False),
)

print("正在调用大模型......")
response = client.chat.completions.create(
    model="deepseek-v4-flash-0731",
    messages=[
        {"role": "user", "content": "你好,请用一句话介绍你自己"},
    ],
    stream=True,   # 关键: 流式返回, response 变成逐块输出的迭代器
    temperature=0.9,
)

print("模型回复(流式输出):")
for chunk in response:
    # 首块可能没有 choices / 只有 role 没有 content, 两层判断防崩溃
    if chunk.choices and chunk.choices[0].delta.content:
        print(
            chunk.choices[0].delta.content,
            end="",      # 中文不要用空格分隔词块
            flush=True,  # 每收一块立刻刷出, 打字机效果
        )
print()  # 流结束补换行
