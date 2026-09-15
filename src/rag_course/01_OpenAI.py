from pathlib import Path
import sys

import httpx
from openai import OpenAI

# 防止 Windows 控制台 GBK 编码打不出 emoji/特殊字符
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 密钥放在项目根目录的 apikey.txt 里 (已加入 .gitignore, 不会被推到 GitHub)
API_KEY = (Path(__file__).resolve().parents[2] / "apikey.txt").read_text(encoding="utf-8").strip()

client = OpenAI(
    api_key=API_KEY,
    base_url="https://tokenfreevip.cc.cd/v1",
    timeout=60,
    # 不走系统代理: 本机 127.0.0.1:7890 代理对该站点 TLS 握手异常, 直连正常
    http_client=httpx.Client(trust_env=False),
)

print("正在调用大模型......")
response = client.chat.completions.create(
    model="qwen3.8-flash",
    messages=[
        {
            "role": "system",
            "content": "你是猫娘"
        },
        {
            "role": "user",
            "content": "hello,你是谁？"
        }
    ],
    stream=False,
    temperature=0.9,
)

print("模型回复:")
print(response.choices[0].message.content)
