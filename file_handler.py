#file_handler：文件处理工具，计算文件的md5，
# 获取文件的文件列表（需要判断是否符合二元组里的格式），读取txt和pdf文件
import os
import hashlib
from utils.path_tool import get_absolute_path
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

#计算文件的md5值
def get_file_md5_hex(file_path:str)->str:
    filepath = get_absolute_path(file_path)
    #检查文件是否存在，文件路径是否正确
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    if os.path.isdir(file_path):
        raise IsADirectoryError(f"路径是一个目录，而不是文件: {file_path}")
    md5_obj = hashlib.md5()
    chunk_size = 4096  # 4KB分片，避免文件过大爆内存
    try:
        with open(filepath, "rb") as f:  # 必须二进制读取
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)
        md5_hex = md5_obj.hexdigest()
        return md5_hex
    except Exception as e:
        print(f"计算文件 {filepath} md5 失败，{str(e)}")
        return None
#返回文件夹内的文件列表（允许的文件后缀）
def listdir_with_allowed_type(path:str,allowed_types:tuple[str]): 
    dir_path = get_absolute_path(path)
    file = []
    if not os.path.isdir(dir_path):
        raise NotADirectoryError(f"{path} 不是文件夹")
    for f in os.listdir(dir_path):
        if f.endswith(allowed_types):
            file.append(os.path.join(dir_path,f))
    return tuple(file)

def pdf_loader(filepath:str,passwd=None)->list[Document]:

    filepath = get_absolute_path(filepath)
    return PyPDFLoader(filepath,passwd).load()

def txt_loader(filepath:str)->list[Document]:
    filepath = get_absolute_path(filepath)
    return TextLoader(filepath,encoding="utf-8").load()

if __name__ == "__main__":
    print(txt_loader("data/rag_data.txt"))