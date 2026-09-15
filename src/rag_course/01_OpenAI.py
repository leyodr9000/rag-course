from pathlib import Path
import sys

import httpx
from openai import OpenAI

# 防止 Windows 控制台 GBK 编码打不出 emoji/特殊字符
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 密钥放在项目根目录的 apikey.txt 里 (已加入 .gitignore, 不会被推到 GitHub)
API_KEY = (Path(__file__).resolve().parents[2] / "apikey.txt").read_text(encoding="utf-8").strip()

# 人设提示词: 同样从项目根目录加载 (已加入 .gitignore, 不会被推到 GitHub)
SYSTEM_PROMPT = (Path(__file__).resolve().parents[2] / "雪菲娅_人格设定.txt").read_text(encoding="utf-8").strip()

client = OpenAI(
    api_key=API_KEY,
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
            "content": "hello,你是谁？"
        }
    ],
    stream=False,
    temperature=0.9,
)

print("模型回复:")
print(response.choices[0].message.content)
