from langchain_community.utilities import SQLDatabase
import pymysql

db_user = "root"
db_password = "HYX20040617"
db_host = "127.0.0.1"
db_name = "SalaryAnalyse"
db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")

def get_schema(_):
    schemas = db.get_table_info()
    return schemas

def get_table_and_field_counts_mysql(host, user, password, database):
    # 连接到数据库
    conn = pymysql.connect(host=host, user=user, password=password, database=database)
    cursor = conn.cursor()

    # 查询所有表名
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()

    table_count = len(tables)
    field_counts = {}
    # 遍历表格，统计字段数
    for table in tables:
        table_name = table[0]
        cursor.execute(f"DESCRIBE {table_name};")
        columns = cursor.fetchall()
        field_counts[table_name] = len(columns)

    # 关闭连接
    cursor.close()
    conn.close()

    return table_count, field_counts



if __name__ == "__main__":
    print(db.get_table_info())