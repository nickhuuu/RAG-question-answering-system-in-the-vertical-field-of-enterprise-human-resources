import os
import json

def load_markdowns(base_path,files):
    """加载原始Markdown内容"""
    # files = {
    #     'target_book': 'performance.json',  # 目标责任书
    #     'summary_report': 'summary.json'  # 年终总结
    # }
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
