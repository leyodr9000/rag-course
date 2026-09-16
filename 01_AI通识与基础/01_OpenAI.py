import os
import sys
from pathlib import Path

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

# 人设提示词: 从项目根目录加载 (已加入 .gitignore, 不会被推到 GitHub)
SYSTEM_PROMPT = (Path(__file__).resolve().parents[1] / "雪菲娅_人格设定.txt").read_text(encoding="utf-8").strip()

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
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": "你好呀，自我介绍一下吧"
        }
    ],
    stream=False,
    temperature=0.9,
)

print("模型回复:")
# print(response.choices[0].message.content)
print(response)
