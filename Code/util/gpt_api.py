import os
from openai import OpenAI

client = OpenAI(
    api_key="",
)

completion = client.chat.completions.create(
    model="gpt-4o-mini", # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    messages=[
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': '你是谁？'}
        ]
)

print(completion.choices[0].message.content)