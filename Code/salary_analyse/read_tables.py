import pandas as pd
import os
from util.qwen_api import qwen_response
from util.deepseek_api import ds_response

def extract_table_headers(path:str) -> list:
    try:
        df = pd.read_excel(path,header=1,nrows=1,engine='openpyxl')
        if df.columns.str.contains("Unnamed").sum() > len(df.columns) // 2 or df.columns.str.match(
                r"^\d+$").sum() > len(df.columns) // 2:
            return df[df.columns[0]]
        return df.columns.values
    except:
        print(f"{path}出错\n")

def traverse_dir(path:str) -> list:
    for root,dirs,files in os.walk(path):
        return files

def find_table(path:str) -> str:
    files = traverse_dir(path)
    content = """请你帮我在这些文件中找出该集团有关于董事、监事、高级管理人员及核心技术人员的薪酬情况，直接返回文件名称，无需任何前言。⾸先，要仔细看看⽤户提供的每个⽂件的内
                    容。⾸先，⽤户给了⼀⻓串⽂件名和对应的内容，⼤部分是 Excel 表格。每个⽂件后⾯跟着的列表是表格中的列名或内容。我的任务是从这些列名中识别出哪些⽂件可能包含薪
                    酬信息。薪酬通常与⼈员职务、薪酬情况、领取薪酬等关键词相关。⽐如，⽂件中如果有“薪酬”、“领取薪酬”、“职务”等列名，可能包含相关信息。需要逐⼀检查每个⽂件的列名。
                    例如：['姓名', '现任职务', '2019 年从本公司领取','薪酬情况（万元）']，明确提到了“薪酬情况”\n"""
    for file in files:
        header = extract_table_headers(path + '/' + file)
        content = content + file + ":" + str(header) + '\n'
    ans = qwen_response(content)
    print("关于薪酬情况的表格：", ans)
    print()
    return path+'/'+ans

if __name__ == '__main__':
    path = "./tables/杭州热电_extracted_tables"
    files = traverse_dir(path)
    content = """请你帮我在这些文件中找出该集团有关于董事、监事、高级管理人员及核心技术人员的薪酬情况，直接返回文件名称，无需任何前言。⾸先，要仔细看看⽤户提供的每个⽂件的内
                容。⾸先，⽤户给了⼀⻓串⽂件名和对应的内容，⼤部分是 Excel 表格。每个⽂件后⾯跟着的列表是表格中的列名或内容。我的任务是从这些列名中识别出哪些⽂件可能包含薪
                酬信息。薪酬通常与⼈员职务、薪酬情况、领取薪酬等关键词相关。⽐如，⽂件中如果有“薪酬”、“领取薪酬”、“职务”等列名，可能包含相关信息。需要逐⼀检查每个⽂件的列名。
                例如：['姓名', '现任职务', '2019 年从本公司领取','薪酬情况（万元）']，明确提到了“薪酬情况”\n"""
    for file in files:
        header = extract_table_headers(path+'/'+file)
        content = content + file + ":" + str(header) + '\n'
    ans = qwen_response(content)
    print("通义千问：",ans)
    print()



