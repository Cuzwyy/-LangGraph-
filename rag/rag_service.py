#总结服务类RagSummarizeService：用户提问，
# 搜索参考资料，将提问和参考资料提交给模型，让模型总结回复。
# 职责：提供"检索器"和"生成链"，供 LangGraph 的 retrieve / respond 节点调用。
from model.factory import chat_model
from rag.vector_store import VectorStoreService
from prompt.react_prompt_template import get_rag_prompt_template
from langchain_core.output_parsers import StrOutputParser

class RagSummarizeService:
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.retriever = self.vector_store.get_retriever()
        self.chat_model = chat_model
        self.prompt_template = get_rag_prompt_template()
        self.chain = self.prompt_template | self.chat_model | StrOutputParser()

    # 按查询检索前 k 个相关文档，支持按 metadata 过滤（如 user_id）
    def get_retriever_docs(self, query: str, filter=None):
        return self.retriever.invoke(query, filter=filter)
