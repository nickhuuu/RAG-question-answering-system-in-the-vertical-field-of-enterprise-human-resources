import pdfplumber
import pandas as pd
from tqdm import tqdm
import os


def extract_all_table(pdf):
    output_dir_tables = './tables/杭州热电_extracted_tables'
    os.makedirs(output_dir_tables, exist_ok=True)
    temp_table = None
    tables = []
    for page in tqdm(pdf.pages[1:]):
        text = page.extract_text()
        page_num = eval(text.strip().split("\n")[-1].split("-")[-1])  # 文本最后一行为页码
        if len(page.extract_tables()) == 0:
            continue
        else:
            # print("--------------- 第{}页 --------------".format(page_num))
            num_table = len(page.extract_tables())
            for table_id in range(num_table):
                table = page.extract_tables()[table_id]
                if temp_table is not None and table_id == 0:  # 上页有可能没结束的表
                    if page.bbox[3]-page.find_tables()[table_id].bbox[1] + 70 >= page.chars[0].get('y1'):  # 该表是页首（-30代表去掉空隙，是针对招股书pdf设计的特定值）
                        # df = pd.DataFrame(table[1:], columns=table[0])  # TODO: 判断是否有表头，有的话可能要合并表头
                        # 与temp拼合
                        df = pd.DataFrame(table)
                        temp_table = pd.concat([temp_table, df], axis=0)
                        if page.chars[-1].get('y0') < page.bbox[3] - page.find_tables()[table_id].bbox[3]:  # 该表不是页尾，结束拼接，加入table_list，temp置空
                            tables.append(temp_table)
                            temp_table = None
                        else:  # 该表是页尾，继续拼接下一页表格
                            break
                    else:  # 该表不是页首，上页页尾表格结束，加入table_list
                        tables.append(temp_table)
                        temp_table = None
                        if page.chars[-1].get('y0') < page.bbox[3] - page.find_tables()[table_id].bbox[3]:  # 该表不是页尾，直接加入table_list
                            df = pd.DataFrame(table)
                            tables.append(df)
                            table_name = []
                        else:  # 该表是页尾，存入temp
                            temp_table = pd.DataFrame(table)
                else:  # temp无值（上个表页尾不是表）
                    if page.chars[-1].get('y0') < page.bbox[3] - page.find_tables()[table_id].bbox[3]:  # 该表不是页尾，直接加入table_list
                        df = pd.DataFrame(table)
                        tables.append(df)
                        table_name = []
                    else:  # 该表是页尾，存入temp
                        temp_table = pd.DataFrame(table)
    for i, table in enumerate(tables):
        excel_filename = os.path.abspath(output_dir_tables) + f"/{i}.xlsx"
        table.to_excel(excel_filename, index=False)
    return


if __name__ == "__main__":
    pdf_path = "./pdf/杭州热电.pdf"
    pdf = pdfplumber.open(pdf_path)
    extract_all_table(pdf)
