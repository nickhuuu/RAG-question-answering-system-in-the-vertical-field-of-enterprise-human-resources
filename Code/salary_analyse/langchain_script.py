import json

#连接数据库
from util.database_connect import db,get_schema

#连接大模型
from util.qwen_api import llm_tongyi

#prompt
from langchain_core.prompts import ChatPromptTemplate

from main import app


question = "介绍一下王文明的信息"


@app.get("/salary_analysis")
def salary_analyse(question:str) -> dict[str, str]:
    template = """根据所输入的数据库架构，其中包含table name,field name,编写一个SQL查询来回答用户的问题，
    其中，查询的内容可以直接用*来表示，即 查询全部内容，不需要'''sql ''' 前缀与后缀：
    {schema}

    问题:{question}
    SQL查询格式：
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", "给定一个输入问题，将其转换为SQL查询，如果遇到复杂情况，可以拆分问题，直接返回查询语句，不需要markdown代码格式返回"),
        ("human", template)
    ])

    # Chain to query
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnablePassthrough

    sql_response = (
            RunnablePassthrough.assign(schema=get_schema)
            | prompt
            | llm_tongyi.bind(stop=["\nSQLResult:"])
            | StrOutputParser()
    )

    query = sql_response.invoke({"question": question})

    print(f"SQL查询语句为：{query}")
    template1 = """根据下表架构、问题、SQL查询和SQL响应以及需要的返回格式，编写问题答案，只返回答案，薪资单位为万元，不需要响应的格式前言：
    {schema}

    问题：{question}
    SQL查询:{query}
    SQL响应：{response}
    答案：
    """

    prompt_response = ChatPromptTemplate.from_messages([
        ("system", "给定一个输入问题和SQL响应，将其转换为自然语言，无前言："),
        ("human", template1)
    ])

    full_chain = (
            RunnablePassthrough.assign(query=sql_response)
            | RunnablePassthrough.assign(schema=get_schema,
                                         response=lambda x: db.run(x["query"]), )
            | prompt_response
            | llm_tongyi
    )

    answer = full_chain.invoke({"question": question})
    dic = {"question": question, "response": answer}
    return dic


if __name__ == "__main__":
    answer = salary_analyse("副总经理有几人，他们是谁，他们的平均薪资是多少")
    print(answer)