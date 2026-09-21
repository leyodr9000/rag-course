import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)
"""
    向量存储服务
    西安创建向量存储的文件，在内部实现向量存储服务的核心类VectorStoreService，并且在该类中创建一恶搞指定检索器的函数
"""
from langchain_chroma import Chroma
import config_data as config

class VectorStoreService(object):
    def __init__(self,embedding):
        """
            embedding:嵌入模型的传入
        """
        self.embedding = embedding

        self.vector_store = Chroma(
            collection_name=config.COLLECTION_NAME,
            embedding_function=self.embedding,
            persist_directory=config.PERSIST_DIRECTORY
        )

    def get_retriever(self):
        """返回向量检索器，方便加入chain"""
        return self.vector_store.as_retriever(search_kwargs={"k":config.SIMILARITY_THRESHOLD})

if __name__ == '__main__':
    from langchain_community.embeddings import DashScopeEmbeddings

    retriever = VectorStoreService(DashScopeEmbeddings(model="text-embedding-v4")).get_retriever()
    result = retriever.invoke("我的体重180斤，尺码推荐")
    print(result)