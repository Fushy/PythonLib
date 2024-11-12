# if not os.path.exists(pathname):
#     Path(pathname).mkdir(parents=True, exist_ok=True)
import os
from pathlib import Path

SEP = os.sep

# def get_current_folder_path():
#     return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def join(path_a, path_b) -> Path:
    return Path(os.path.join(path_a, path_b))

# p.with_name("file" + p.name)
# save_model_path.parent.joinpath(save_model_path.stem + "_history.plk")
