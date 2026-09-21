import time
import streamlit as st
from rag import RagService
import config_data as config

# 标题
st.title("智能管家")
# 分隔符
st.divider()

rag_service = RagService()

if "message" not in st.session_state:
    st.session_state["message"] = [{"role":"assistant","content":"你好，有什么可以帮助你的吗?"}]

if "rag" not in st.session_state:
    # 此时就可以维护一个RagService对象
    st.session_state["rag"] = RagService()

for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

# 在页面的下方提供用户的输入栏
prompt = st.chat_input()
if prompt:
    # 在页面输出用户的提问
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role":"user","content":prompt})

    ai_result_list = []
    with st.spinner("AI思考中...."):
        # result_stream是流对象不能当做字符串进行存储
        result_stream = st.session_state["rag"].chain.stream({"input":prompt},config.SESSION_CONFIG)

        def capture(generator,cache_list):
            for chunk in generator:
                # yield表达式的作用是返回迭代器
                cache_list.append(chunk)
                yield chunk
        time.sleep(1) # 假设AI思考1秒钟
        # write_stream的参数是一个迭代器
        st.chat_message("assistant").write_stream(capture(result_stream,ai_result_list))
        # 含义：将list里面所有的字符串都链接为一个整体字符串，每个片段之间使用空字符串进行连接
        st.session_state["message"].append({"role": "assistant", "content": "".join(ai_result_list)})

# ["a","b","c"]  "".join(list) --> abc