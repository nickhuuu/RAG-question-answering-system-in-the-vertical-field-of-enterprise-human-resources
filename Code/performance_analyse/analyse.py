from util.deepseek_api import ds_response
from main import app
import os
import json

def load_markdowns(base_path,files):
    """加载原始Markdown内容"""
    # files = {
    #     'target_book': 'performance.json',  # 目标责任书
    #     'summary_report': 'summary.json'  # 年终总结
    # }u
    contents = {}
    for name, filename in files.items():
        path = os.path.join(base_path, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"关键文件缺失：{filename}")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                contents[name] = data.get("result", {}).get("markdown", "")
        except Exception as e:
            raise ValueError(f"文件读取失败 {filename}: {str(e)}")
    if len(contents) != 2:
        raise ValueError("必须提供目标责任书和年终总结两个文件")
    return contents['target_book'], contents['summary_report']


@app.get("/performance_analyse")
def analyze_performance(target_filepath:str, summary_filepath:str) -> str:
    files = {
        'target_book': target_filepath,  # 目标责任书
        'summary_report': summary_filepath  # 年终总结
    }
    target_md, summary_md = load_markdowns("./",files)
    """核心分析方法"""
    prompt = f"""请根据以下材料进行结构化绩效考核评估：

    [目标责任书内容]
    {target_md}

    [员工年终总结]
    {summary_md}

    请严格按以下JSON格式返回结果：
    {{
        "total_score": 总分（保留1位小数）,
        "score_details": [
            {{
                "indicator": 指标名称,
                "weight": 权重（0-1之间的小数）,
                "completion_rate": 完成率（0-1之间的小数）,
                "score": 得分（保留1位小数）
            }},
            ...更多指标
        ],
        "improvement_suggestions": [
            "建议1",
            "建议2"
        ]
    }}

    要求：
    1. 只返回JSON，不要额外文字
    2. 权重总和必须为1
    3. 总分等于各指标得分之和
    4. 不要输出'''json '''
    """
    messages = [{"role": "user", "content": prompt}]
    answer = ds_response(messages)
    return answer


    # try:
    #     result = json.loads(response.choices[0].message.content)
    #     # 数据校验
    #     if not isinstance(result.get("total_score"), (int, float)):
    #         raise ValueError("总分格式错误")
    #     if not all(isinstance(item, dict) for item in result.get("score_details", [])):
    #         raise ValueError("得分明细格式错误")
    #     return result
    # except json.JSONDecodeError:
    #     raise ValueError("大模型返回结果解析失败")



if __name__ == "__main__":
    ans = analyze_performance()
    print(ans)