import requests
import json
from util.api_keys import text_in_ocr_app_id,text_in_ocr_app_secret
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

class TextinOcr(object):
    def __init__(self, app_id, app_secret):
        self._app_id = app_id
        self._app_secret = app_secret
        self.host = 'https://api.textin.com'

    def recognize_pdf2md(self, image_path, options, is_url=False):
        """
        pdf to markdown
        :param options: request params
        :param image_path: string
        :param is_url: bool
        :return: response

        options = {
            'page_start': 0,
            'page_details': 0,  # 不包含页面细节信息
            'table_flavor': 'md',
            'get_image': 'none',
            'parse_mode': 'auto',  # 解析模式设为scan
        }
        """
        url = self.host + '/ai/service/v1/pdf_to_markdown'
        headers = {
            'x-ti-app-id': self._app_id,
            'x-ti-secret-code': self._app_secret
        }
        if is_url:
            image = image_path
            headers['Content-Type'] = 'text/plain'
        else:
            image = get_file_content(image_path)
            headers['Content-Type'] = 'application/octet-stream'

        return requests.post(url, data=image, headers=headers, params=options)


if __name__ == "__main__":
    textin = TextinOcr(text_in_ocr_app_id, text_in_ocr_app_secret)

    path = "./data"  # 请将pdf文件放在ZjuProject/data/目录下
    to_path = "./data/1"  # 输出目录，需确保已存在
    file_names = ["5.传出神经系统药理.pdf"]
    for file_name in file_names:
        file_path = f"{path}/{file_name}"
        resp = textin.recognize_pdf2md(file_path, {
            'table_flavor': 'md',
            'parse_mode': 'auto',  # 设置解析模式为auto模式
        })
        print(f"{file_name}:request time:", resp.elapsed.total_seconds());
        result = json.loads(resp.text)
        with open(f'{to_path}/{file_name}.json', 'w', encoding='utf-8') as fw:
            json.dump(result["result"]["markdown"], fw, indent=4, ensure_ascii=False)