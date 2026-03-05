from humanfriendly.terminal import output


def split_txt(input_file, output_prefix, chunk_size=50, overlap=10):
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read().replace("\n", "")  # 读取文本并去除换行符

    length = len(text)
    index = 0
    part = 1

    while index < length:
        chunk = text[index:index + chunk_size]
        output_file = f"{output_prefix}{part}.txt"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(chunk)

        print(f"生成文件: {output_file}")

        index += (chunk_size - overlap)  # 移动索引，保持 10 字重叠
        part += 1


if __name__ == "__main__":
    output_path = "/rag/年报/东风汽车2019/"
    input_file = "/txt/东风汽车2019.txt"
    split_txt(input_file, output_path,chunk_size=200,overlap=20)
