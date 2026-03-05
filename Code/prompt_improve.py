import json

from util.deepseek_api import ds_response
from prompt import prompt
from main import app

@app.get("/upe")
def upe_qa(file_path:str) -> dict[str,str]:
    with open(file_path,'r',encoding='utf-8') as f:
        file_content = f.read()
    content = ""
    content += prompt
    content += "这是关于岗位评估的prompt"

    # content += eg1
    #
    # content += """以上是你之前评估的结果，包含“思考过程”“答案”，同时我还加上了“专家给出的标准答案一项”"""

    content += """以下是一份具体的岗位说明书，请你根据岗位评估的prompt，进行岗位评估"""

    content += file_content

    message = [
        {"role": "user", "content": content},
    ]

    response = ds_response(message)
    ans = {
        "file_path": file_path,
        "file_content": file_content,
        "response": response,
    }
    return ans

if __name__ == "__main__":
    file_path = "./json文件/岗位说明书（json）/集团财务部/财务管理部-融资主管-岗位说明书.json"
    ans = upe_qa(file_path)
    print(ans)

