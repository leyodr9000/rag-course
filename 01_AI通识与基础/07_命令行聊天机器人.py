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
base_url = os.getenv("TOKENRHYTHM_BASE_URL")
if not api_key:
    raise RuntimeError("未读取到 TOKENRHYTHM_API_KEY, 请检查项目根目录 .env 文件")

client = OpenAI(
    api_key=api_key,
    base_url=base_url,
    timeout=60,
    # 不走系统代理: 本机 127.0.0.1:7890 代理对该站点 TLS 握手异常, 直连正常
    http_client=httpx.Client(trust_env=False),
)

# 历史消息列表: 多轮对话保留上下文的关键, 每轮对话都往里追加
messages = [
    {"role": "system", "content": "你是一个热心的AI助手"},
]

print("=" * 50)
print("命令行聊天机器人 (输入 exit 退出)")
print("=" * 50)

# 主循环: 连续多轮对话
while True:
    try:
        user_input = input("\n你: ").strip()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C / Ctrl+Z 也能正常退出
        print("\n机器人: 再见!")
        break

    if not user_input:
        continue
    if user_input.lower() == "exit":
        print("机器人: 再见!")
        break

    # 1. 把用户输入追加到历史消息
    messages.append({"role": "user", "content": user_input})

    # 2. 调用模型 (流式输出, 打字机效果)
    print("机器人: ", end="", flush=True)
    response = client.chat.completions.create(
        model="deepseek-v4-flash-0731",
        messages=messages,
        stream=True,
        temperature=0.9,
    )

    # 3. 流式打印回复, 同时拼接完整回复 (稍后要存进历史)
    reply = ""
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            reply += content
            print(content, end="", flush=True)
    print()

    # 4. 把机器人的回复也追加到历史 (保留上下文的关键一步!)
    messages.append({"role": "assistant", "content": reply})
