"""
    基于Streamlit实现WEB网页上传服务
    安装依赖：uv add streamlit
    Streamlit：当WEB网页元素发生变化，则代码重新执行一遍，代码重新执行一遍则会导致状态的丢失
    此时基于streamlit官方提供的组件，即：session_state会话状态记录器
"""
import os
import time

import streamlit as st
from dotenv import load_dotenv

load_dotenv()  # 加载 .env, 否则 DashScopeEmbeddings 读不到 DASHSCOPE_API_KEY

from knowledge_base import KnowledgeBaseService

# 添加网页标题
st.title("知识库更新服务")

# file_uploader
uploader_file = st.file_uploader(
    "请上传TXT文件",
    type=["txt"],
    accept_multiple_files=False,# False表示仅接受一个文件的上传
)

# 创建知识库更新服务类对象
serice = KnowledgeBaseService()
# session_state就是一个字典
if "service" not in st.session_state:
    st.session_state["service"] = KnowledgeBaseService()

if uploader_file is not None:
    # 提取文件的信息
    file_name = uploader_file.name
    file_type = uploader_file.type
    file_size = uploader_file.size / 1024 # KB

    st.subheader(f"文件名：{file_name}")
    # 可以在浏览器中显示正常大小的文本
    st.write(f"格式：{file_type} | 大小：{file_size:.2f} KB")

    # get_value --> bytes
    text = uploader_file.getvalue().decode("utf-8")
    # st.write(text)

    with st.spinner("载入知识库中...."):
        time.sleep(1) # 为了保证用户的体验，数字1表示1秒钟
        result = st.session_state['service'].upload_by_str(text, file_name)
        st.write(result)

# print(f"上传了{st.session_state['counter']}个文件")














