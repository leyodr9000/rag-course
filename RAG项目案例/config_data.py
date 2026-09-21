MD5_PATH = "./md5.text"

# Chroma
COLLECTION_NAME = "rag"
PERSIST_DIRECTORY = "./chroma_db"

# spliter
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100
SEPARATORS = ["\n\n","\n",".","!","?","。","，","！","？"," ",""]
# 文本分割的阈值
MAX_SPLIT_CHAR_NUMBER = 1000

SIMILARITY_THRESHOLD = 1 # 检索返回匹配的文档数量

EMBEDDING_MODEL_NAME = "text-embedding-v4"
CHAT_MODEL_NAME = "qwen3.8-flash"

SESSION_CONFIG = {
    "configurable":{
        "session_id" : "user_001"
    }
}