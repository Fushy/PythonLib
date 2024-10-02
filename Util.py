import itertools
from collections.abc import Iterable
from datetime import datetime, timedelta
from hashlib import blake2b
import os
import string
import sys
from time import sleep
from typing import Callable, Container

from pandas import DataFrame
from pandas import Series
import pandas as pd
import pyperclip
import sympy
from sympy import Eq
from sympy.parsing.sympy_parser import parse_expr
from cryptography.fernet import Fernet

from Files import run_cmd
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
                + "\ !#$%&()-@^_`{}~+,.;=[]\n")  # do not change "\ " it disables space character on command line


# utils ascii chars https://emojipedia.org/fr/
# ⬛⬜
# ♛♕♘♞♖♜♝♗


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
    if isinstance(element, Iterable) and not isinstance(element, str):
        return True
    return False


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


def export_requirements(path_to_python_exe=None, output="requirements"):
    path = "--python " + path_to_python_exe + " " if path_to_python_exe is not None else ""
    cmd = "pip {}freeze > {}".format(path, output)
    run_cmd(cmd)


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


if __name__ == '__main__':
    # export_requirements(r"A:\Programmes\Python\Python3.11\python.exe",
    #                     r"B:\_Documents\Pycharm\Util\util_requirements.txt")
    # install_requirements(r"A:\Programmes\Python\Python3.11\python.exe",
    #                      r"B:\_Documents\Pycharm\Util\util_requirements.txt")
    # upgrade_requirements(r"A:\Programmes\Python\Python3.11\python.exe",
    #                      r"B:\_Documents\Pycharm\Util\util_requirements.txt")
    # print(encrypt_string(""))
    print_numspace(1654168546646.4186548)
    export_conda_env()
