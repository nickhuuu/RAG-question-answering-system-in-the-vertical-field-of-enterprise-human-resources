from util.deepseek_api import ds_response

def upe_qa(upe_file_path):
    content = "先理解下面的几个关于UPE岗位评估的文件，后面我会给你具体的职位评估表进行职位评估"
    file_names = ["UPE五因素的定义.json", "UPE五因素解释表.json", "因素1-影响因素点数对照表.json",
                  "因素2-沟通因素对照表.json", "因素3-创新因素对照表.json"]
    path = "./json文件"

    for file_name in file_names:
        file_path = f"{path}/{file_name}"
        with open(file_path, 'r', encoding='utf-8') as f:
            content += file_name + '\n'
            content += f.read()
        content += "\n"

    message = [
        {"role": "user", "content": content},
    ]

    res1 = ds_response(message)
    message.append({'role': 'assistant', 'content': res1})
    print("理解提示词：")
    content = ('根据以下UPE岗位评估提示词以及输入的岗位说明书，根据提示词的内容，给出具体的评分，'
               '其中，精神风险不计入。注意贡献程度以贡献比例为优先标准，不以编制人数为标准。适当降低沟通频率。在影响力方面，'
               '除部门部长之外评分需略降低，若需依赖上级部门或部长，则评分需略降低。若为分公司，则影响力评分适当降低。'
               '只返回各个评分，不用返回具体原因。')
    from prompt import prompt
    content += "提示词："
    content += prompt

    with open(upe_file_path, 'r', encoding='utf-8') as fw:
        content += "岗位说明书：\n"
        content += fw.read()

    message.append({"role": "user", "content": content})

    print()
    print("评估：")
    res2 = ds_response(message)
    message.append({'role': 'assistant', 'content': res2})

    #return res2

    while True:
        question = input("请用户输入问题：")
        if question != "":
            message.append({"role": "user", "content": question})
            print(message)
            res = ds_response(message)
            message.append({'role': 'assistant', 'content': res})
            print()

if __name__ == '__main__':
    upe_qa("./json文件/岗位说明书（json）/集团财务部/财务部-财务部长-岗位说明书.json")
