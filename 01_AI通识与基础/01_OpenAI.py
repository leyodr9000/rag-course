import sys
from pathlib import Path

import httpx
from openai import OpenAI

# 防止 Windows 控制台 GBK 编码打不出 emoji/特殊字符
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 密钥和人设都在项目根目录 (本文件在 项目根/01_AI通识与基础/ 下, parents[1] 即项目根)
API_KEY = (Path(__file__).resolve().parents[1] / "apikey.txt").read_text(encoding="utf-8").strip()
SYSTEM_PROMPT = (Path(__file__).resolve().parents[1] / "雪菲娅_人格设定.txt").read_text(encoding="utf-8").strip()

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
            "content": "你好呀，自我介绍一下吧"
        }
    ],
    stream=True,
    temperature=0.9,
)

print("模型回复(流式输出):")
# stream=True 时 response 是一个迭代器, 每迭代一次吐出一小段 (chunk)
for chunk in response:
    # 防 IndexError: 最开始可能有 choices 为空的 chunk
    # 防 None: 第一个 chunk 往往只带 role 不带内容, delta.content 为 None
    if chunk.choices and chunk.choices[0].delta.content:
        print(
            chunk.choices[0].delta.content,
            end="",      # 中文不要用 " " 做分隔, 否则每个词块之间会被塞进空格
            flush=True,  # 每收到一小块立刻强制刷出, 实现"打字机"效果
        )
print()  # 流结束后补一个换行, 让光标回到行首
