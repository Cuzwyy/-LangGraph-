from model.factory import embed_model
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.config_handler import chroma_config
from utils.path_tool import get_absolute_path
import os
from utils.file_handler import get_file_md5_hex, listdir_with_allowed_type, pdf_loader, txt_loader

# VectorStoreService：封装 Chroma 向量库的「初始化 + 检索 + 建库」三件事。
# 建库时用 md5 去重，避免同一文件被重复入库。
class VectorStoreService:
    def __init__(self):
        # 初始化向量数据库
        self.vector_db = Chroma(
            collection_name=chroma_config["collection_name"],          # 集合名
            embedding_function=embed_model,
            persist_directory=chroma_config["persist_directory"],      # 本地持久存储
        )
        # 初始化切分器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_config['chunk_size'],
            chunk_overlap=chroma_config['chunk_overlap'],
            length_function=len,
            separators=chroma_config['separates']
        )

    # 获取检索器
    def get_retriever(self):
        return self.vector_db.as_retriever(search_kwargs={'k': chroma_config["k"]})

    # 存储 md5
    def save_md5(self, md5_hex: str):
        md5_path = get_absolute_path(chroma_config["md5_hex_store"])
        with open(md5_path, "a", encoding="utf-8") as f:   # "a" = 追加模式
            f.write(md5_hex + "\n")
            print(f"已保存文件的md5到 {md5_path}")
    # 检查 md5 是否已存在，已处理过则返回 True
    def check_md5(self, md5_hex: str) -> bool:
        md5_path = get_absolute_path(chroma_config["md5_hex_store"])
        if not os.path.exists(md5_path):
            open(md5_path, "w", encoding="utf-8").close()  # 创建文件
            return False
        with open(md5_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip() == md5_hex:
                    return True
        return False

    # 从数据文件夹读取文件、切分、入库（带 md5 去重）
    def load_documents(self, file_path: str):
        files = listdir_with_allowed_type(file_path, allowed_types=tuple(chroma_config["allow_knowledge_file_type"]))
        i = 1
        for f in files:
            f_md5 = get_file_md5_hex(f)
            if self.check_md5(f_md5):
                print(f"文件 {f} 已处理过，跳过。")
                continue
            if f.endswith(".pdf"):
                documents = pdf_loader(f)
            else:
                documents = txt_loader(f)
            # 切分文档
            split_docs = self.text_splitter.split_documents(documents)
            self.vector_db.add_documents(split_docs)
            self.save_md5(f_md5)
            print(f"第 {i} 个文件已处理并存入向量库。")
            i += 1

if __name__ == "__main__":
    vector_store_service = VectorStoreService()
    vector_store_service.load_documents(chroma_config["data_path"])
