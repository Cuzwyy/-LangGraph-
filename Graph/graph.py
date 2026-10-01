"""
generate_query → retrieve → respond
（查询改写）    （检索）   （生成）
用户输入问题字符串
        ↓
【generate_query】根据对话历史生成/优化检索查询
        ↓
【retrieve】用生成的查询去检索器拉取相关文档
        ↓
【respond】把「检索到的文档 + 对话上下文」交给大模型
        ↓
输出最终回答字符串
"""
from langchain_core.messages import HumanMessage
from typing import TypedDict
from rag.rag_service import  RagSummarizeService
from langgraph.graph import StateGraph,START,END,MessagesState
from model.factory import chat_model
from prompt.query_prompt import QUERY_SYSTEM_PROMPT
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from prompt.react_prompt_template import  get_rag_prompt_template
rag_service = RagSummarizeService()
from langchain_core.messages import AIMessage
from pydantic import BaseModel
from langgraph.checkpoint.postgres import PostgresSaver
class SearchQuery(BaseModel):
    query: str
#定义长期数据库,链接rag这个表
DB_URL = "  "

#定义全局状态
class OverALLState(MessagesState):
    query :str
    answer: str
    docs : list
class OutputState(TypedDict):
    answer: str
#定义查询改写节点，
def generate_query(state:OverALLState):
    messages = state["messages"]
    #回答一次的情况，拿当前的消息去查询
    if len(messages) ==0:
        raise ValueError("消息列表不能为空，请先传入用户的问题")
    if len(messages) ==1:
        #单轮：没有上下文，直接用原话
        user_query = messages[0].content
    else:
        #多轮：把「最新提问 + 完整对话历史」一起给模型改写
        model= chat_model
        latest_question = messages[-1].content   # 用户最新提问
        #定义个提示词模板
        prompt = ChatPromptTemplate.from_messages([
           ("system",QUERY_SYSTEM_PROMPT),
           ("placeholder", "{messages}")
        ])
        #创建链,并实现结构化输出
        chain = prompt | model.with_structured_output(SearchQuery)
        result = chain.invoke({
            "messages": messages,          # 完整对话历史（进 placeholder）
            "user_query": latest_question, # 最新提问（进 system 里的 {user_query}）
        })
        user_query = result.query

    return {
        "query": user_query
        }
#调用retriever-去检索相关文档
#定义检索节点
def retrieve(state:OverALLState):
    query = state["query"]
    return {
        "docs": rag_service.get_retriever_docs(query)
        }

#获取消息列表，把输出字符串
def respond(state:OverALLState):
    docs = state["docs"]
    context = ""
    counter = 0
    for doc in docs:
        counter += 1
        context += f"【参考资料{counter}】: 参考资料：{doc.page_content} | 参考元数据：{doc.metadata}\n"
    query =state["query"]
    model= chat_model
    prompt_template = get_rag_prompt_template()
    chain = prompt_template | model | StrOutputParser()
    user_answer = chain.invoke(
        {
            "input" :query,
            "context" : context
        }
    )
    return {
        "answer" :user_answer,
         "messages": [AIMessage(content=user_answer)]
    }
#创建图
builder = StateGraph(
    state_schema=OverALLState,
    output_schema=OutputState,
)
#添加节点
builder.add_node("generate_query", generate_query)
builder.add_node("retrieve", retrieve)
builder.add_node("respond", respond)
#添加边
builder.add_edge(START, "generate_query")
builder.add_edge("generate_query", "retrieve")
builder.add_edge("retrieve", "respond")
builder.add_edge("respond", END)
with PostgresSaver.from_conn_string(DB_URL) as checkpointer:
    checkpointer.setup()   # 首次运行自动建 checkpoint 所需的表（重复执行无副作用）
    #编译图
    graph = builder.compile(checkpointer=checkpointer)
    #指定线程
    config = {
        "configurable" :{
            "thread_id" : "chapter01"
        }
    }
    #运行图
    result = graph.invoke({"messages" : [
        HumanMessage(content="金毛的性格")
    ]}, config)["answer"]

    print(result)
