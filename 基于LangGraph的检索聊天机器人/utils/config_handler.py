import yaml
from utils.path_tool import get_absolute_path
#参数获取文件
def load_chroma_config(config_path: str = get_absolute_path("config/chroma.yml"), encoding: str = "utf-8"):
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)

def load_model_config(config_path: str = get_absolute_path("config/model.yml"), encoding: str = "utf-8"):
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)



chroma_config = load_chroma_config()
model_config = load_model_config()


if __name__ == "__main__":
    print(model_config['chat_model'])