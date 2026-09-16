import os
import sys
import json

import httpx
from dotenv import load_dotenv
from openai import OpenAI

# 防止 Windows 控制台 GBK 编码打不出 emoji/特殊字符
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 加载环境变量 (项目根目录的 .env, 已加入 .gitignore, 不会被上传)
load_dotenv()

# 1. 获取 API Key 并初始化客户端
api_key = os.getenv("TOKENRHYTHM_API_KEY")
if not api_key:
    raise RuntimeError("未读取到 TOKENRHYTHM_API_KEY，请检查项目根目录 .env 文件")

client = OpenAI(
    api_key=api_key,
    base_url="https://tokenrhythm.studio/v1",
    timeout=60,
    # 不走系统代理：本机 127.0.0.1:7890 代理对该站点 TLS 握手异常，直连正常
    http_client=httpx.Client(trust_env=False),
)

# 2. 定义需要抽取的字段结构
schema = ['日期', '股票名称', '开盘价', '收盘价', '成交量']

# 3. 准备示例数据（Few-shot 学习）
examples_data = [
    {
        "content": "2023-01-10，股市震荡，股票强大科技今日开盘价100rmb，一度飙升至105rmb",
        "answers": {
            "日期": "2023-01-10",
            "股票名称": "强大科技A股",
            "开盘价": "100人民币",
            "收盘价": "102人民币",
            "成交量": "520000",
        }
    },
    {
        "content": "2024-05-16，股市利好，股票英伟达美股今日开盘价105美元，一度飙升至109美元，随后回落至100美元，最终以116美元收盘，成交量达到3560000。",
        "answers": {
            "日期": "2024-05-16",
            "股票名称": "英伟达美股",
            "开盘价": "105美元",
            "收盘价": "116美元",
            "成交量": "3560000",
        }
    }
]

# 分类列表 (原代码中定义了但后续逻辑未直接使用，保留)
examples_types = ['新闻报道', '财务报告', '公司公告', '分析师报告']

# 4. 准备提问数据
questions = [
    "2025-06-16，股市利好，股票传智教育A股今日开盘价66人民币，一度飙升至70人民币，随后回落至65人民币，最终以68人民币收盘，成交量达到123000。",
    "2025-06-06，股市利好，股票黑马程序员A股今日开盘价200人民币，一度飙升至211人民币，随后回落至201人民币，最终以206人民币收盘。",
]

# 5. 初始化对话历史（包含 System Prompt）
messages = [
    {"role": "system", "content": f"你帮我完成信息抽取，我给你句子，你抽取{schema}信息，按照JSON字符串输出，如果某些信息不存在，用'原文未提及显示'"}
]

# 6. 将示例数据加入对话历史（修复了原图列表调用 .items() 的错误）
for example in examples_data:
    # 将字典格式的 answers 转换为 JSON 字符串
    assistant_content = json.dumps(example["answers"], ensure_ascii=False)
    messages.append({"role": "user", "content": example["content"]})
    messages.append({"role": "assistant", "content": assistant_content})

# 7. 向模型循环提问
for q in questions:
    response = client.chat.completions.create(
        model="qwen3.8-flash",
        # 将当前提问追加到历史消息后面
        messages=messages + [{"role": "user", "content": f"按照示例，回答这段文本的信息抽取：{q}"}],
    )
    
    # 打印模型的回答结果
    print(f"提问内容：{q}")
    print(f"模型回复：{response.choices[0].message.content}\n")
