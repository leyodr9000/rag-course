import json
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

# 提取目标字段 (schema), 注意要和示例 answers 里的键一致, 别漏了"开盘价"
schema = ['日期', '股票名称', '开盘价', '收盘价', '成交量']

# 示例数据: content 是原文, answers 是模型应该输出的标准答案
# (注意: 示例里的事实必须和原文一致, 日期/数值抄错会教坏模型)
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

# 提问数据 (第2条和示例2很像但日期不同, 用来检验模型是真的在抽取还是照抄示例)
questions = [
    "2025-06-16，股市利好，股票传智教育A股今日开盘价66人民币，一度飙升至70人民币，随后回落至65人民币，最终以68人民币收盘，成交量达到3560000。",
    "2025-06-06，股市利好，股票英伟达美股今日开盘价105美元，一度飙升至109美元，随后回落至100美元，最终以116美元收盘，成交量达到3560000。",
]

#原始发送方式（附加历史消息）
"""
[
    {"role": "system",      "content": "你是金融专家，从文本中提取['日期', '股票名称', ...]字段，缺失填'未知'，只输出JSON 下面有示例："},

    {"role": "user",        "content": "2023-01-10，股市震荡，股票强大科技............."},
    {"role": "assistant",   "content": "{\"日期\": \"2023-01-10\", ...}"},

    {"role": "user",        "content": "要提问的问题"}
]
"""

messages = [
{"role": "system",
 "content": f"你是金融专家，从文本中提取{schema}这几个字段的值，文本里没有提到的字段填'未知'，只输出一个JSON对象，不要输出任何其他内容。下面有示例："},
]

#示例同样组织成 user(原文) + assistant(JSON答案) 一对
for example in examples_data:
    messages.append({"role": "user", "content": example["content"]})
    messages.append({"role": "assistant", "content": json.dumps(example["answers"], ensure_ascii=False)})

#向模型提问
for i, q in enumerate(questions, 1):
    response = client.chat.completions.create(
        model="deepseek-v4-flash-0731",
        # f 格式化字符串
        messages=messages+[{"role":"user","content":f"按照示例，提取这段文本中的字段信息：{q}"}]
    )
    #注意: 打印要放在循环里, 放在循环外只会留下最后一个问题的结果
    print(f"问题{i}提取结果:")
    print(response.choices[0].message.content)
    print()
