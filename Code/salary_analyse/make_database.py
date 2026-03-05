import pymysql
from read_tables import find_table
from util.qwen_api import qwen_response
import pandas as pd


def mysql_insert(path:str) -> str:
    file_path = find_table(path)
    df = pd.read_excel(file_path)
    content = f"""{file_path}:这是关于董事、监事、高级管理人员及核心技术人员的薪酬情况的表格{str(df)}，
                我需要制作一个数据库，现在已经有了salary表格，它有id,name,company,position,salary四个列，
                id：主键，自增，确保每条记录唯一。
                name：姓名，VARCHAR(50) 类型，限制最多50个字符，不能为空。
                company:公司，VARCHAR(50),记录公司名称，不能为空
                position：职位，VARCHAR(50) 类型，不能为空。
                salary：薪酬，DECIMAL(10,2) 类型，确保存储两位小数的工资数据，不能为空,若表格里没有记录，则salary列返回0。
                你需要帮我写一个SQL插入语句，插入姓名、岗位、薪酬。
                直接返回语句，无需返回其他前言,不需要'''sql ''' 前缀与后缀"""
    res = qwen_response(content)
    return res

path = "./tables/杭州热电_extracted_tables"

conn = pymysql.connect(host='localhost',
                       port=3306,
                       user='root',
                       database='SalaryAnalyse',
                       passwd='Lch20040904')

# 创建游标
cursor = conn.cursor()

exec_statement = mysql_insert(path)
print(exec_statement)

cursor.execute(exec_statement)
conn.commit()

# 关闭连接
cursor.close()
conn.close()

