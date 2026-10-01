# 作用：集中创建聊天模型和文本向量模型。
#
# 待实现的类：
# - BaseModelFactory：抽象工厂，规定子类提供 generator 方法；
# - ChatModelFactory：创建 ChatTongyi 聊天模型；
# - EmbeddingsFactory：创建 DashScopeEmbeddings 向量模型。
#
# 待实现的方法：
# - generator：由不同子类实现具体模型的创建逻辑。
#
# 最终要向其他模块提供 chat_model 和 embed_model 两个可复用实例。
# 配置来源：utils.config_handler 中的 model_config（model.yml）。
# 理解重点：业务代码不直接负责模型构造，模型名称由 YAML 配置决定。
from abc import ABC, abstractmethod
from typing import Optional
import os
from langchain_community.embeddings import ZhipuAIEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_community.chat_models.tongyi import BaseChatModel
from langchain_deepseek import ChatDeepSeek
from utils.config_handler import model_config
from dotenv import load_dotenv
load_dotenv(override=True)

class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        pass



class ChatModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return ChatDeepSeek(
            model=model_config["chat_model"],
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            api_base=os.getenv("DEEPSEEK_BASE_URL"),
            extra_body={"thinking": {"type": "disabled"}},
        )


class EmbeddingsFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return ZhipuAIEmbeddings(
            model=model_config["embedding_model"],
            api_key=os.getenv("ZHIPUAI_API_KEY"),
        )



chat_model = ChatModelFactory().generator()

embed_model = EmbeddingsFactory().generator()
if __name__ == '__main__':
    #print(chat_model.invoke("你好"))
    vector = embed_model.embed_query("你好，世界")
    print("向量维度：", len(vector))