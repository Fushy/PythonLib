# import chardet
#
# with open('filename.txt', 'rb') as f:
#     result = chardet.detect(f.read())
#
# encoding = result['encoding']
# with open('filename.txt', encoding=encoding) as f:
#     content = f.read()
import os
import shutil
import psutil
from pathlib import Path, WindowsPath
from pickle import dump, load
from typing import Callable, Optional

def create_folder(folder):
    """Create a folder and print a message if it was created."""
    folder = Path(folder)  # Convertir en Path si c'est un str
    if not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created folder: {folder}")


def get_running_python_scripts() -> list[str]:
    scripts = []

    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info['cmdline']

                if cmdline:
                    # Chercher après --file (pour PyCharm/debuggers)
                    if '--file' in cmdline:
                        file_index = cmdline.index('--file')
                        if file_index + 1 < len(cmdline):
                            scripts.append(cmdline[file_index + 1])
                            continue

                    # Sinon chercher le premier .py qui n'est pas un helper
                    for item in cmdline:
                        if item and isinstance(item, str) and item.endswith('.py'):
                            # Ignorer les helpers PyCharm/debuggers
                            if 'pydev' not in item.lower() and 'helper' not in item.lower():
                                scripts.append(item)
                                break
        except (psutil.NoSuchProcess, psutil.AccessDenied, Exception):
            continue

    return scripts


def create_directory(relative_path: str) -> None:
    target_dir = Path(relative_path)
    target_dir.mkdir(parents=True, exist_ok=True)


def save_obj_to_file(obj, file_name: Path):
    assert file_name.suffix == ".plk" and type(file_name) is WindowsPath
    path_name = file_name.parent
    if not is_file_exists(path_name):
        os.makedirs(path_name, exist_ok=True)
    with open(file_name.as_posix(), 'wb') as file:
        dump(obj, file)


def get_obj_from_file(file_name):
    with open(file_name + ".plk", 'rb') as file:
        return load(file)


def is_file_exists(path) -> bool:
    """ Due to concurrency, after an is_existing call, it may be possible that the file doesn't exist,
    in this case, use a try-catch exception when the file is used """
    return os.path.exists(path)


def is_pattern_file_exists(folder: str, pattern: str) -> bool:
    """
    Check if a file matching the regex pattern exists in the given folder.

    Args:
        folder: Path to the folder to search in
        pattern: Regex pattern to match filenames against

    Returns:
        True if at least one file matches the pattern, False otherwise
    """
    import re
    from pathlib import Path

    folder_path = Path(folder)

    # Check if folder exists
    if not folder_path.exists() or not folder_path.is_dir():
        return False

    # Compile the regex pattern
    regex = re.compile(pattern)

    # Check each file in the folder
    for file_path in folder_path.iterdir():
        if file_path.is_file() and regex.search(file_path.name):
            return True

    return False


def is_dir(path: str) -> bool:
    return os.path.isdir(path)


def is_file(path: str) -> bool:
    return os.path.isfile(path)


def get_files_from_path(*paths: str | WindowsPath, _filter: Callable[[str], bool] = None, recursive: bool = False) -> list[str]:
    import glob
    files = []
    for path in paths:
        files += glob.glob(str(path) + r"\*.*")
        if recursive:
            files += glob.glob(str(path) + r"\**\*.*", recursive=recursive)
    if _filter is not None:
        files = list(filter(_filter, files))
    return files


def get_current_files(_filter: Callable[[str], bool] = None, recursive: bool = False) -> list[str]:
    cwd = os.getcwd()
    files = get_files_from_path(cwd, _filter=_filter, recursive=recursive)
    # print("Files in %r: %s" % (cwd, files))
    return files


def get_last_modified_datetime(file):
    return datetime.fromtimestamp(os.path.getmtime(file))


def get_first_line(file_name: str, encoding="utf-8") -> Optional[str]:
    try:
        with open(file_name, 'r', encoding=encoding) as file:
            return file.readline()
    except FileNotFoundError:
        return None


def get_first_part(file_name):
    return file_name[:file_name.rfind(os.sep) + 1]


def get_last_part(file_name):
    return file_name[file_name.rfind(os.sep) + 1:file_name.rfind(".")]


def get_ext(file_name):
    return file_name[file_name.rfind(".") + 1:]


def get_file(file_name: str, encoding="utf-8") -> Optional[str]:
    try:
        with open(file_name, 'r', encoding=encoding) as file:
            return file.read()
    except FileNotFoundError:
        return None


def get_lines(file_name: str, encoding="utf-8") -> Optional[list[str]]:
    lines = get_file(file_name, encoding)
    if lines:
        return lines.splitlines()
    # try:
    #     with open(file_name, 'r', encoding=encoding) as file:
    #         return file.readlines()
    # except FileNotFoundError:
    #     return None


def count_lines(file_name: str) -> int:
    return sum([1 for _ in open(file_name)])


def overwrite(file_name: str, value: str, encoding="utf-8", mode="w"):
    if "b" in mode:
        with open(file_name, mode) as file:
            file.write(str(value))
    else:
        with open(file_name, mode, encoding=encoding) as file:
            file.write(str(value))


def append(file_name: str, value: str, encoding="utf-8", mode="a+"):
    if "b" in mode:
        with open(file_name, mode) as file:
            file.write(value)
    else:
        with open(file_name, mode, encoding=encoding) as file:
            file.write(value)


def delete(file_name: str):
    try:
        os.remove(file_name)
    except (FileNotFoundError, PermissionError) as e:
        pass


def move_to(file_name: str, dest: str):
    shutil.move(file_name, dest)


def concat_files(dest, *args):
    lines = []
    for file in args:
        file_lines = get_lines(file)
        if file_lines is not None:
            lines.extend(file_lines)
    overwrite(dest, "".join(lines))


def sort_file(file_name, dest, blacklist_lines=None):
    if blacklist_lines is None:
        blacklist_lines = [""]
    blacklist_lines = [line + "\n" for line in blacklist_lines]
    sorted_file = sorted(filter(lambda x: x not in blacklist_lines, get_lines(file_name)))
    overwrite(dest, "".join(sorted_file))


def remove_same_lines(file_name, dest=None):
    if dest is None:
        dest = file_name
    lines = get_lines(file_name)
    new_lines = []
    for i in range(len(lines)):
        if lines[i] not in lines[i + 1:]:
            new_lines.append(lines[i])
    overwrite(dest, "".join(new_lines))


def output(*args, log_file=None, end="\n"):
    concat_args = " ".join([arg for arg in args]) + end
    if log_file is None:
        print(concat_args)
    else:
        append(log_file, concat_args)


def is_ascii(text):
    return all(ord(char) < 128 for char in text)


def equivalent_text(text1: str, text2: str) -> bool:
    """
    Check if two texts are equivalent by normalizing them.

    Normalization rules:
    - Convert to lowercase
    - Replace spaces with hyphens
    - Remove special characters

    Examples:
        equivalent_text("White Flare", "white-flare") -> True
        equivalent_text("EX Delta Species", "ex-delta-species") -> True
        equivalent_text("Sun & Moon", "sun-moon") -> True

    Args:
        text1: First text to compare
        text2: Second text to compare

    Returns:
        True if texts are equivalent, False otherwise
    """
    import re

    def normalize(text):
        # Convert to lowercase
        text = text.lower()
        # Replace spaces with hyphens
        text = text.replace(" ", "-")
        # Remove special characters (keep only alphanumeric and hyphens)
        text = re.sub(r'[^a-z0-9\-]', '', text)
        # Remove multiple consecutive hyphens
        text = re.sub(r'-+', '-', text)
        # Remove leading/trailing hyphens
        text = text.strip('-')
        return text

    return normalize(text1) == normalize(text2)


def run_file(file):
    os.system('"' + file + '"')


def run_cmd(cmd):
    os.system('"' + cmd + '"')


if __name__ == '__main__':
    dest = "anglais.txt"
    sort_file(dest, dest=dest)
    remove_same_lines(dest)
