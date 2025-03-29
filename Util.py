import itertools
import string
import subprocess
from collections.abc import Iterable
from datetime import datetime, timedelta
from hashlib import blake2b
from io import BytesIO
from pathlib import Path
from sys import stderr
from time import sleep
from typing import Callable, Container
from urllib.parse import quote, unquote

import pandas as pd
import pyperclip
import sympy
import yaml
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from pandas import DataFrame, Series
from sympy import Eq
from sympy.parsing.sympy_parser import parse_expr

from Files import is_file_exists, run_cmd
from Introspection import frameinfo
from Times import now

# set Util as a library on Pycharm : Interpreter Paths
#     File -> Settings... -> Project -> Python Interpreter -> Python Interpreter list: or Gear symbol -> Scroll down until Show all ->
#     Tree folder icon -> + select the Util folder -> done

# # https://developer.microsoft.com/fr-fr/microsoft-edge/tools/webdriver/
# # https://stackoverflow.com/questions/14684968/how-to-export-virtualenv
# # pip install --upgrade pip
# # pip install --upgrade setuptools
# # pip install --upgrade pip setuptools
# # pip install --upgrade pip setuptools wheel
# # pip install numpy
# # pip install wheel
# # pip install python-telegram-bot
# # pip install python-telegram-bot --upgrade
# # pip install python-telegram-bot
# # pip install ffmpeg-python
# # pip install pydub
# # pip install selenium
# # pip install msedge-selenium-tools
# # pip install requests-html
# # pip install http-request-randomizer
# # pip install screeninfo
# # pip install termcolor
# # pip install gtts
# # pip install pyinstaller
# # pip install pyperclip
# # pip install mysql-connector-python
# # pip install simpleaudio
# # pip install gtts  https://ffmpeg.org/download.html#build-windows http://blog.gregzaal.com/how-to-install-ffmpeg-on-windows/
# # pip install simpleaudio   sinon la lecture avec gtts n'est pas possible (PermissionError: [Errno 13] Permission denied) https://visualstudio.microsoft.com/visual-cpp-build-tools/
# # if something is wrong
# # https://www.lfd.uci.edu/~gohlke/pythonlibs/

# from util_bot import SEED_PATH_1, SEED_PATH_2


COMMON_CHARS = (string.ascii_lowercase
                + string.ascii_uppercase
                + string.digits
                + "\\ !#$%&()-@^_`{}~+,.;=[]\n")  # do not change "\ " it disables space character on command line


# utils ascii chars https://emojipedia.org/fr/
# ⬛⬜
# ♛♕♘♞♖♜♝♗

def getenv(key):
    script_directory = frameinfo(2)["pathname"]
    dotenv_path = os.path.join(script_directory, '.env')
    if not is_file_exists(dotenv_path):
        print(dotenv_path, "does not exist", file=stderr)
    value = os.getenv(key)
    if value is None:
        load_dotenv(dotenv_path=dotenv_path)
        value = os.getenv(key)
    return value


def image_from_clipboard():
    try:
        import PIL.ImageGrab
        image = PIL.ImageGrab.grabclipboard()
        if image is not None and hasattr(image, 'size'):
            return image
        return None
    except Exception:
        return None


def print_directory_tree(directory='.', prefix='', max_depth=None, current_depth=0, save_to_file=False):
    path = Path(directory)
    output = []
    if current_depth == 0:
        line = f"{path.name}/"
        print(line)
        if save_to_file:
            output.append(line)
    if max_depth is not None and current_depth >= max_depth:
        return output
    items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
    for i, item in enumerate(items):
        connector = '└── ' if i == len(items) - 1 else '├── '
        line = f'{prefix}{connector}{item.name}'
        print(line)
        if save_to_file:
            output.append(line)

        if item.is_dir():
            new_prefix = prefix + ('    ' if i == len(items) - 1 else '│   ')
            output.extend(print_directory_tree(item, new_prefix, max_depth, current_depth + 1, save_to_file))
    if current_depth == 0 and save_to_file:
        with open('paths.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(output))
    return output


def read_image(file_name):
    with open(file_name, 'rb') as file:
        return BytesIO(file.read())


def make_url_clickable(url: str) -> str:
    return quote(url, safe=':/?=')


def make_url_redable(url: str) -> str:
    return unquote(url, safe=':/?=')


def dict_to_obj_type(d):
    return type("Object", (), d)()


def get_obj_file():
    run_cmd("conda env export > packages.yml")


def export_conda_env():
    run_cmd("conda env export > packages.yml")


def chronometer(seconds, pre="", extra=""):
    start = now()
    elapsed = (now() - start).total_seconds()
    while elapsed < seconds:
        elapsed = (now() - start).total_seconds()
        if (seconds - elapsed) > 5.1:
            sleep(5)
            print(pre, "{:.2f}".format(seconds - elapsed), extra)
        elif (seconds - elapsed) < 0.2:
            sleep(0.1)
            print(pre, "{:.2f}".format(seconds - elapsed), extra)
        else:
            sleep(2)


def dict_retire_none(dictionnary):
    return {key: value for key, value in dictionnary.items() if value is not None}


def polish_df(df: DataFrame, normalize_column: str = None):
    if normalize_column is not None:
        df[normalize_column] = normalize(df[normalize_column])
    df.index = list(range(1, len(df) + 1))
    return df


def normalize(obj: list | Series):
    if type(obj) is Series:
        min_val = obj.min()
        max_val = obj.max()
        return (obj - min_val) / (max_val - min_val)
    elif type(obj) is list:
        min_val = min(obj)
        max_val = max(obj)
        return [(x - min_val) / (max_val - min_val) for x in obj]


def print_numspace(num) -> str:
    if type(num) is int:
        integer_part = str(num)
        fractional_part = ""
    elif type(num) is float:
        num = f"{num:.10f}".rstrip('0').rstrip('.')
        integer_part, fractional_part = num.split('.')
    numspace = '_'.join(integer_part[::-1][i:i + 3] for i in range(0, len(integer_part), 3))[::-1]
    # numspace += "." + ' '.join(fractional_part[i:i+3] for i in range(0, len(integer_part), 3))
    if fractional_part != "":
        numspace += "." + fractional_part
    return numspace


def flatten_2d_list(lst):
    return [item for sublist in lst for item in sublist]


def solve(equation):
    """
    2x => 2*x
    2^x => Pow(2, x)
    """
    assert "=" in equation
    left, right = map(parse_expr, equation.split("="))
    eq = Eq(left, right)
    return sympy.solve(eq)


# solve("Pow(2, x)=2")
# solve("2^(2*x+1)+2^(x+3)-10=0")

# def subtitute_var(equation):
#     x = symbols("x")
#     y = symbols("y")
#     return expr.subs(x, 2)

def format_float(value, precision):
    return None if value is None else "{:.{}f}".format(value, precision)


def get_min(a, b, default_value=None):
    default_value = default_value or float('inf')
    return min(a or default_value, b or default_value)


def get_max(a, b, default_value=None):
    default_value = default_value or float('-inf')
    return max(a or default_value, b or default_value)


def string_encoded_to_bytes(str_encoded_raw: str) -> bytes:
    """ '\x80\x04K\x05.' -> b'\x80\x04K\x05.'"""
    return bytes(bytearray(list(map(ord, str_encoded_raw))))


def change_char(text, char, index):
    return text[:index] + char + text[index + 1:]


def restrict_num(x: float, _min: float, _max: float):
    if x < _min:
        x = _min
    if x > _max:
        x = _max
    return x


def is_running_under_basic_console():
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


def reverse_dict(dict_: dict) -> dict:
    """ Reverse the self.questions_answers dictionary. Keys become values, and values become keys """
    new_keys = sorted(set(itertools.chain.from_iterable(dict_.values())))
    return {new_key: [key for (key, values) in dict_.items() if new_key in values] for new_key in new_keys}
    # return {tuple(v) if type(v) is Iterable else v: k for (k, v) in d.items()}


def init_dataframe(columns) -> DataFrame:
    return pd.DataFrame({}.fromkeys(columns, []))


def add_rows_dataframe(df: DataFrame, rows: dict[str, list | tuple], bottom=True) -> DataFrame:
    """ slow, add all lines at the same time"""
    rows = {k: [v] if type(v) not in (list, tuple, set) else v for (k, v) in rows.items()}
    concat_df = [df, pd.DataFrame(rows)][::1 if bottom else -1]
    # return pd.concat(concat_df).drop_duplicates().reset_index(drop=True)
    return pd.concat(concat_df).reset_index(drop=True)


def add_columns_dataframe(df: DataFrame, columns: dict) -> DataFrame:
    """ slow, add all lines at the same time"""
    # np.set_printoptions(suppress=True,
    #                     formatter={'float_kind': '{:0.10f}'.date_format})
    for name, values in columns.items():
        df.insert(len(df.columns), name, values)
    return df


def auto_repr(cls):
    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, ', '.join('%s=%s' % item for item in vars(self).items()))

    cls.__repr__ = __repr__
    return cls


def computer_name():
    import platform
    return platform.node()


def get_pid():
    return os.getpid()


def is_docker() -> bool:
    import os
    return os.path.exists('/.dockerenv')


def get_os() -> str:
    import platform
    if platform.system() == 'Darwin':
        return 'mac'
    elif platform.system() == 'Linux':
        return 'linux'
    elif platform.system() == 'Windows':
        return 'windows'
    else:
        raise NotImplementedError(f'Unsupported OS: "{platform.system()}"')


def get_first_deeply_value(obj: object):
    while isinstance(obj, Container) and type(obj) is not str:
        obj = obj[0]
    return obj


def str_to_hashcode(text: str or list[str], len_hashcode=8, seed=1337, whitelist="") -> list[str] or str:
    if whitelist == "":
        whitelist = string.ascii_letters + string.digits
    if is_iter_but_not_str(text):
        return [str_to_hashcode(txt, len_hashcode, seed, whitelist) for txt in text]
    encode = blake2b()
    if len_hashcode > encode.digest_size * 2 or len(str(seed)) >= 9:
        return ""
    encode.update(bytes(text.encode('utf-8')))
    hashcode = encode.hexdigest()
    hashtext = []
    part_len = (encode.digest_size * 2 // len_hashcode)
    for i in range(len_hashcode):
        txt = hashcode[i * part_len:(i + 1) * part_len]
        num = sum([(ord(c) * seed) for c in txt]) % len(whitelist)
        hashtext.append(whitelist[num])
    return "".join(hashtext)


def str_to_hashdigits(text, len_hashcode=32, seed=1337) -> int:
    whitelist = string.digits
    return int(str_to_hashcode(text, len_hashcode, seed, whitelist))


def generate_key() -> bytes:
    with open(r"B:\_Documents\APIs\fernet_key", 'rb') as file:
        return file.read()
    # return Fernet.generate_key()


def encrypt_string(s: str, key=None) -> bytes:
    if key is None:
        key = generate_key()
    return Fernet(key).encrypt(s.encode())


def decrypt_string(encrypted: bytes, key=None) -> str:
    if key is None:
        key = generate_key()
    return Fernet(key).decrypt(encrypted).decode()


def datetime_to_timedelta(x):
    return x - datetime.strptime("0:0:0", "%H:%M:%S")


def is_iter_but_not_str(element):
    """ Si le type de l'objet peut être parcouru et n'est pas de type str"""
    return isinstance(element, Iterable) and not isinstance(element, str)


def know_connected_wifi_password():
    """netsh wlan show profiles "MAIS_MAROL" key = clear"""


def infinite_sequence():
    num = 0
    while True:
        num += 1
        yield num


def chained_list(*args):
    """ A utiliser lorsqu'il n'y pas d'effet de bord
    :param args:
    :return:
    """
    while True:
        for element in args:
            yield element


def selenium_screenshot(browser, file=""):
    if file == "":
        file = now().strftime("%d-%m-%y %H-%M-%S %Z")
    # save_browser = copy.deepcopy(browser)
    save_browser = browser
    print("screenshot", now().strftime("%d-%m-%y %H-%M-%S %Z"))
    for i in range(len(save_browser.window_handles)):
        save_browser.switch_to.window(save_browser.window_handles[i])
        print("\tscreenshots\\" + file + "_" + str(i) + ".png")
        save_browser.get_screenshot_as_file("screenshots\\" + file + "_" + str(i) + ".png")


def debug_selenium(browser):
    while True:
        selenium_screenshot(browser)
        sleep(0.5)


def sorted_dict(dictionary: dict, key=lambda x: x, reverse=False) -> dict:
    return dict(sorted(dictionary.items(), key=key, reverse=reverse))


def sorted_dict_str(dictionary: dict, key=lambda x: x, reverse=False) -> str:
    result = "{"
    v_is_dict = False
    for k, v in sorted(dictionary.items(), key=key, reverse=reverse):
        if type(v) is dict:
            v_is_dict = True
            v = sorted_dict(v)
        elif type(v) is Iterable:
            v = sorted(v)
        k = str(k)
        if v_is_dict is False:
            v = str(v)
            if v.isalnum() or v.isalpha() or v.isidentifier() or v.isascii():
                result += "\"" + k + "\":\"" + v + "\","
            else:
                result += "\"" + k + "\":" + v + ","
        else:
            v = str(v)
            if v.isalnum() or v.isalpha() or v.isidentifier():
                result += "\"" + k + "\":\"" + v + "\","
            else:
                result += "\"" + k + "\":" + v + ","
    result = list(result)
    result[-1:] = "}"
    return "".join(result)


def repeat_function_binance(fun: Callable, interval_time: timedelta, debug=False, *args):
    """ Une fois que la fonction est terminée, on attend :interval_time:."""
    while True:
        fun()
        if debug:
            print(now().strftime("%Y-%m-%d %H:%M:%S"), "executed successfully", *args)
        sleep(interval_time.total_seconds())


def get_clipboard():
    return pyperclip.paste()


def update_clipboard(text):
    return pyperclip.copy(text)


def wait_clipboard_change():
    clipboard = get_clipboard()
    while clipboard == get_clipboard():
        sleep(0.5)


def action_on_clipboard_update(fun: Callable):
    while True:
        wait_clipboard_change()
        fun()


def two_complement_representation(x: int):
    mask = 2 ** (8 * ((x.bit_length() // 8) + 1)) - 1
    return x & mask


def two_complement_representation_2(x: int):
    shift = 8 * ((x.bit_length() // 8) + 1)
    return x % (1 << shift)


def two_complement_representation_3(x: int):
    from ctypes import c_uint8 as unsigned_byte
    return unsigned_byte(x).value


def create_exe(filename):
    cmd = "pyinstaller {} --onefile".format(filename)
    os.system("cmd /k \"{}\"".format(cmd))


def install_requirements(path_to_python_exe=None, _input="requirements.txt"):
    path = "--python " + path_to_python_exe + " " if path_to_python_exe is not None else ""
    cmd = "pip {}install -r {}".format(path, _input)
    run_cmd(cmd)


def upgrade_requirements(path_to_python_exe=None, _input="requirements.txt"):
    path = "--python " + path_to_python_exe + " " if path_to_python_exe is not None else ""
    cmd = "pip {}install -r {} --upgrade".format(path, _input)
    run_cmd(cmd)


def output(*args, log_file=None, end="\n"):
    concat_args = " ".join([arg for arg in args]) + end
    if log_file is None:
        print(concat_args)
    else:
        file = open(log_file, "a+")
        file.write(concat_args)
        file.close()


# def export_requirements(path_to_python_exe=None, output="requirements"):
#     path = "--python " + path_to_python_exe + " " if path_to_python_exe is not None else ""
#     cmd = "pip {}freeze > {}".format(path, output)
#     run_cmd(cmd)

def export_current_requirements():
    """Creates environment files using pip and conda commands."""
    os.makedirs('packages', exist_ok=True)

    # Generate requirements.txt
    output = subprocess.check_output(['pip', 'freeze']).decode('utf-8')
    lines = [l.strip() for l in output.splitlines() if l.strip() and not l.startswith('#')]
    reqs = [l.split('@')[0].strip() if '@' in l else l for l in lines]
    print("requirements.txt")
    with open('packages/requirements.txt', 'w') as f:
        f.write('\n'.join(reqs) + '\n')

    # Generate environment.yml
    try:
        result = subprocess.run(["conda", "env", "export"], capture_output=True, text=True, check=True)
        print("environment.yml")
        with open("packages/environment.yml", "w") as f:
            f.write('\n'.join(result.stdout.splitlines()[:-1]) + '\n')
    except subprocess.CalledProcessError as e:
        print(f"Error creating environment.yml: {e}")

    # Generate Dockerfile
    print("Dockerfile")
    with open('packages/Dockerfile', 'w') as f:
        f.write(
            'FROM continuumio/miniconda3\nWORKDIR /app\nCOPY environment.yml .\nRUN conda env create -f environment.yml\nSHELL ["conda", "run", "-n", "myenv", "/bin/bash", "-c"]\nCOPY . .\nCMD ["conda", "run", "-n", "myenv", "python", "app.py"]')

    # Generate Pipfile
    print("Pipfile")
    with open('packages/Pipfile', 'w') as f:
        pipfile = '[[source]]\nurl = "https://pypi.org/simple"\nverify_ssl = true\nname = "pypi"\n\n[packages]\n'
        pipfile += ''.join(f'{r.split("==")[0]} = "=={r.split("==")[1]}"\n' if '==' in r else f'{r} = "*"\n' for r in reqs)
        pipfile += '[dev-packages]\n\n[requires]\npython_version = "3.8"'
        f.write(pipfile)

    # Generate setup.py
    print("setup.py")
    with open('packages/setup.py', 'w') as f:
        f.write(f'from setuptools import setup\nsetup(name="my_package", version="0.1", packages=["my_package"], install_requires={reqs})')

    # Generate pyproject.toml
    print("pyproject.toml")
    with open('packages/pyproject.toml', 'w') as f:
        toml = '[tool.poetry]\nname = "my_package"\nversion = "0.1.0"\nauthors = ["Your Name <you@example.com>"]\n\n[tool.poetry.dependencies]\npython = "^3.8"\n'
        toml += '\n'.join(f'{r.split("==")[0]} = "^{r.split("==")[1]}"' if '==' in r else f'{r} = "*"' for r in reqs)
        toml += '\n\n[build-system]\nrequires = ["poetry-core"]\nbuild-backend = "poetry.core.masonry.api"'
        f.write(toml)


import importlib.util

import importlib.util

import ast
import sys
import os
import importlib.util


def export_script_requirements(script_path=__file__, superset_yml=None):
    r""" export_script_requirements(r"A:\Pycharm\Scrapping\test.py", r"A:\Pycharm\Util\packages\environment.yml") """
    processed = set()
    superset_packages = []

    # Load superset YAML with package specifications
    if superset_yml and os.path.exists(superset_yml):
        with open(superset_yml, 'r') as f:
            superset_data = yaml.safe_load(f)
            for item in superset_data.get('dependencies', []):
                if isinstance(item, dict) and 'pip' in item:
                    for pip_pkg in item['pip']:
                        pkg_name = pip_pkg.split('==')[0].split('@')[0]
                        superset_packages.append({
                            'name': pkg_name,
                            'spec': pip_pkg,
                            'source': 'pip'
                        })
                elif isinstance(item, str):
                    pkg_name = item.split('==')[0].split('@')[0]
                    superset_packages.append({
                        'name': pkg_name,
                        'spec': item,
                        'source': 'conda'
                    })

    def _find_best_match(module_name):
        candidates = []
        for pkg in superset_packages:
            if module_name in pkg['name']:
                candidates.append(pkg)
        if not candidates:
            return None
        # Select longest matching package name (most specific match)
        return max(candidates, key=lambda x: len(x['name']))

    def _export_script_requirements(script_path, processed):
        script_dir = os.path.dirname(os.path.abspath(script_path))

        with open(script_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=script_path)

        class ImportVisitor(ast.NodeVisitor):
            def __init__(self):
                self.imports = set()

            def visit_Import(self, node):
                for alias in node.names:
                    self.imports.add(alias.name.split('.')[0])

            def visit_ImportFrom(self, node):
                if node.module is not None:
                    self.imports.add(node.module.split('.')[0])

        visitor = ImportVisitor()
        visitor.visit(tree)
        initial_imports = visitor.imports

        conda_packages = set()
        pip_packages = set()
        queue = []

        def is_stdlib_module(module_name):
            return module_name in sys.stdlib_module_names

        def is_personal_module(origin):
            if not origin:
                return False
            return ('site-packages' not in origin) and ('dist-packages' not in origin)

        # Process initial imports
        for module in initial_imports:
            if not is_stdlib_module(module) and module not in processed:
                queue.append(module)

        while queue:
            current_module = queue.pop(0)
            if current_module in processed:
                continue
            processed.add(current_module)

            # Check for superset matches
            matched_pkg = _find_best_match(current_module)
            if matched_pkg:
                if matched_pkg['source'] == 'conda':
                    conda_packages.add(matched_pkg['spec'])
                else:
                    pip_packages.add(matched_pkg['spec'])
                continue

            # Standard package resolution
            spec = importlib.util.find_spec(current_module)
            if not spec:
                conda_packages.add(current_module)
                continue

            if is_personal_module(spec.origin):
                # Recursive processing for local modules
                module_file = spec.origin
                try:
                    sub_conda, sub_pip = _export_script_requirements(module_file, processed)
                    conda_packages.update(sub_conda)
                    pip_packages.update(sub_pip)
                except Exception as e:
                    conda_packages.add(current_module)
            else:
                conda_packages.add(current_module)

        return conda_packages, pip_packages

    # Create output directory
    packages_dir = 'packages'
    os.makedirs(packages_dir, exist_ok=True)

    # Generate package lists
    conda_pkgs, pip_pkgs = _export_script_requirements(script_path, processed)

    # Write YAML file
    yaml_path = os.path.join(packages_dir, 'script.yml')
    with open(yaml_path, 'w') as f:
        f.write("name: myenv\n")
        f.write("channels:\n  - defaults\n")
        f.write("dependencies:\n")

        # Always include pip as a conda dependency if we have pip packages
        if pip_pkgs:
            f.write("  - pip\n")

        # Write conda packages
        for pkg in sorted(conda_pkgs):
            f.write(f"  - {pkg}\n")

        # Write pip packages if any
        if pip_pkgs:
            f.write("  - pip:\n")
            for pkg in sorted(pip_pkgs):
                f.write(f"    - {pkg}\n")


if __name__ == '__main__':
    # export_requirements(r"A:\Programmes\Python\Python3.11\python.exe",
    #                     r"B:\_Documents\Pycharm\Util\util_requirements.txt")
    # install_requirements(r"A:\Programmes\Python\Python3.11\python.exe",
    #                      r"B:\_Documents\Pycharm\Util\util_requirements.txt")
    # upgrade_requirements(r"A:\Programmes\Python\Python3.11\python.exe",
    #                      r"B:\_Documents\Pycharm\Util\util_requirements.txt")
    # print(encrypt_string(""))
    export_current_requirements()
    # export_script_requirements(r"/PlayrightBrowser.py", r"A:\Pycharm\Util\packages\environment.yml")
    # conda env create --name temp --file script.yml
