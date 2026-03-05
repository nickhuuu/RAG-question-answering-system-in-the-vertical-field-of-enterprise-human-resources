import dashscope
from openai import OpenAI
from util.api_keys import dashscope_apikey
from langchain_community.llms import Tongyi
client = OpenAI(
    api_key=dashscope_apikey,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

def qwen_response(content):
    # 创建聊天完成请求
    completion = client.chat.completions.create(
        model="qwen-max-0125",
        messages= [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {"role": "user", "content": content},
        ]
    )
                
    return completion.choices[0].message.content

dashscope.api_key = dashscope_apikey
llm_tongyi = Tongyi(model = 'qwen-max-0125',dashscope_api_key = dashscope_apikey)

if __name__ == "__main__":
    llm_tongyi.invoke("你好，请介绍一下你自己")




