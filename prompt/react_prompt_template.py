from langchain_core.prompts import PromptTemplate

def get_rag_prompt_template():
    """RAG 总结专用模板:占位符只有 {context} 和 {input}。"""
    return PromptTemplate.from_template(
        """
        请根据以下参考资料，直接、确定地回答用户的问题。

        要求：
        1. 直接给出答案，不要使用"如果""可能""大概""也许"等不确定措辞。
        2. 如果问题里有指代词（如"它""这个"），请根据上下文自然理解其指代，直接回答，不要反复确认或质疑指代对象。
        

        参考资料:
        {context}

        用户问题: {input}

        回答:
        """
    )
