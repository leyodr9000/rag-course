import sys
from pathlib import Path

import httpx
from openai import OpenAI

# 防止 Windows 控制台 GBK 编码打不出 emoji/特殊字符
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 复用 01 的配置: 密钥在项目根目录 apikey.txt (本文件在 项目根/01_AI通识与基础/ 下, parents[1] 即项目根)
API_KEY = (Path(__file__).resolve().parents[1] / "apikey.txt").read_text(encoding="utf-8").strip()

client = OpenAI(
    api_key=API_KEY,
    base_url="https://tokenrhythm.studio/v1",
    timeout=60,
    # 不走系统代理: 本机 127.0.0.1:7890 代理对该站点 TLS 握手异常, 直连正常
    http_client=httpx.Client(trust_env=False),
)

print("正在调用大模型......")
response = client.chat.completions.create(
    model="qwen3.7-max",
    messages=[
        # system: 设定身份; 之后的 user/assistant 交替就是把历史对话原样带上,
        # 模型全靠这些历史记录才有"记忆", 不带的话它根本不知道小明小红养了什么
        {"role": "system", "content": "你是一个AI助理，回答很简洁"},
        {"role": "user", "content": "小明有两条宠物狗"},
        {"role": "assistant", "content": "好的"},
        {"role": "user", "content": "小红有三只宠物猫"},
        {"role": "assistant", "content": "好的"},
        {"role": "user", "content": "总共有几只宠物？"}
    ],
    # 开启流式输出
    stream=True,
    temperature=0.9
)
print("成功调用大模型......")

# 3、处理结果: response 是逐块输出的迭代器
for chunk in response:
    # 首块可能没有 choices / 只有 role 没有 content, 两层判断防崩溃
    if chunk.choices and chunk.choices[0].delta.content:
        print(
            # 截取流式输出的消息片段
            chunk.choices[0].delta.content,
            end="",      # 中文词块之间不要塞空格 (材料里的 " " 会把中文切碎)
            flush=True,  # 立刻刷新缓冲区
        )
print()  # 流结束补换行
