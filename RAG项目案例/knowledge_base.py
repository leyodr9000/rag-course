import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)

"""
    知识库
"""
import os
import config_data as config
import hashlib
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime

def check_md5(md5_str: str):
    """
        检查传入的md5字符串是否已经被处理过
        return False表示md5未处理过  return True表示md5已经处理过，已有记录
    """
    if not os.path.exists(config.MD5_PATH):
        # if条件进入则表示文件不存在，那肯定没有处理过这个MD5
        # w称之为操作符，表示写操作、r表示读操作
        open(config.MD5_PATH, 'w',encoding="utf-8").close()
        return False
    else: # 文件已存在
        for line in open(config.MD5_PATH,'r',encoding="utf-8").readlines():
            line = line.strip() # 处理字符串前导及尾部的空白区域（空格+回车）
            if line == md5_str:
                # 说明已经处理过了
                return True
        return False


def save_md5(md5_str: str):
    """将传入的md5字符串，记录到文件内保存。操作符a表示追加，如果使用w则会覆盖"""
    with open(config.MD5_PATH,'a',encoding="utf-8") as f:
        f.write(md5_str + "\n")

def get_string_md5(input_str: str,encoding="utf-8"):
    """
        将传入的字符串转换为md5字符串
        通过hashlib可以计算字符串的md5值
    """
    # 将字符串转换为bytes字节数组
    str_bytes = input_str.encode(encoding=encoding)
    # 创建MD5对象
    md5_obj = hashlib.md5() # 得到MD5对象
    md5_obj.update(str_bytes) # 更新内容（传入即将要转换的字节数组）
    md5_hex = md5_obj.hexdigest() # 得到MD5的十六进制字符串
    return md5_hex


class KnowledgeBaseService(object):
    def __init__(self): # Python类的初始化语法

        # 如果目录不存在则创建，如果存在则跳过
        os.makedirs(config.PERSIST_DIRECTORY,exist_ok=True)

        self.chroma = Chroma(
            collection_name=config.COLLECTION_NAME, # 向量数据库的表名
            embedding_function=DashScopeEmbeddings(model="text-embedding-v4"),
            persist_directory=config.PERSIST_DIRECTORY # 数据库本地存储文件夹
        ) # 向量存储的实例Chroma向量库对象


        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE, # 分割之后的文本段最大长度
            chunk_overlap=config.CHUNK_OVERLAP, # 连续文本段之间的字符重叠数
            separators=config.SEPARATORS, # 自然段落划分的符号
            length_function=len # 使用Python自带的len函数做长度统计的依据
        ) # 文本分割器的对象

    def upload_by_str(self,data,filename):
        """将传入的字符串进行向量化，存入向量数据库中"""
        # 1、先得到传入字符串的MD5值
        md5_hex = get_string_md5(data)
        if check_md5(md5_hex):
            # 已经存在
            return "[跳过]内容已经存在知识库中!"
        if len(data) > config.MAX_SPLIT_CHAR_NUMBER:
            knowledge_chunks: list[str] = self.spliter.split_text(data)
        else:
            knowledge_chunks = [data]

        # metadata表示元数据
        metadata = {
            "source":filename,
            "create_time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator":"臣哥"
        }

        # 本质上一个迭代器
        self.chroma.add_texts( # 内容就被加载到向量数据库中
            knowledge_chunks,
            # 通过列表推导式组装每一份数据共享同一份元数据
            metadata=[metadata for _ in knowledge_chunks],
        )

        #
        save_md5(md5_hex)
        return "[成功]内容已经成功载入向量库!"

if __name__ == '__main__':
    service = KnowledgeBaseService()
    r = service.upload_by_str("林俊杰","testfile")
    print(r)

"""
    基于st_session_status作为中转，让这两部分的代码连接在一起
    即：会在app_file_uoloader类中存储一份KnowledgeBaseService的实例，调用KnowledgeBaseService实例中的upload_by_str完成完成文件上传
"""
