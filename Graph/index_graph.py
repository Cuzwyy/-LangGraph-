"""
知识库构建：读取数据目录下的文件，切分后加载进向量数据库。
流程：fetch_documents（读取文件列表） → index_documents（入库）
输入：数据存放的地址
结果：文档进入向量数据库
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from rag.vector_store import VectorStoreService
from collections.abc import Sequence
from langchain_core.documents import Document
from utils.config_handler import chroma_config
from utils.file_handler import listdir_with_allowed_type, pdf_loader, txt_loader

# 定义全局状态
class OverALLState(TypedDict):
    docs: Sequence[Document]
    file_path: str

# 定义输入状态
class InputState(TypedDict):
    file_path: str

# 节点一：传入文档地址，获取文档列表
def fetch_documents(state: InputState):
    filepath = state['file_path']
    files = listdir_with_allowed_type(filepath, tuple(chroma_config["allow_knowledge_file_type"]))
    all_docs = []
    for f in files:
        if f.endswith(".pdf"):
            docs = pdf_loader(f)
        else:
            docs = txt_loader(f)
        all_docs.extend(docs)
    return {"docs": all_docs}

# 节点二：把文档加载进向量数据库
def index_documents(state: OverALLState):
    vector_store_service = VectorStoreService()
    split_docs = vector_store_service.text_splitter.split_documents(state['docs'])
    vector_store_service.vector_db.add_documents(split_docs)
    print("已成功加载进向量数据库！")
    return {}

# 创建图
builder = StateGraph(state_schema=OverALLState, input_schema=InputState)
builder.add_node("fetch_documents", fetch_documents)
builder.add_node("index_documents", index_documents)
builder.add_edge(START, "fetch_documents")
builder.add_edge("fetch_documents", "index_documents")
builder.add_edge("index_documents", END)
graph = builder.compile()
document = graph.invoke({"file_path": chroma_config['data_path']})
