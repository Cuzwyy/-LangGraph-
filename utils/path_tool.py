#为整个项目提供绝对路径
import os
def get_file_path():
    #先获取当前文件的绝对路径
    current_path = os.path.abspath(__file__)
    #获取当前文件所在目录的绝对路径
    current_dir = os.path.dirname(current_path)
    #获取整个项目的绝对路径
    project_path = os.path.dirname(current_dir)
    return project_path

#获取当前相对路径在整个项目中的绝对路径
def get_absolute_path(relative_path:str)->str:
    project_path = get_file_path()
    absolute_path = os.path.join(project_path, relative_path)
    return absolute_path

if __name__ == "__main__":
    print(get_absolute_path("utils/path_tool.py"))