from inspect import currentframe, getargvalues
import os.path
from pathlib import Path
import sys
from time import sleep
from typing import Optional

def get_variable_name(variable):
    callers_local_vars = currentframe().f_back.f_locals.items()
    return [var_name for var_name, var_val in callers_local_vars if var_val is variable][0]


def get_current_abspath() -> Path:
    return Path(os.path.abspath(os.getcwd()))


def get_current_path() -> Path:
    return Path(os.getcwd())


def get_current_file_name(depth=2) -> str:
    return frameinfo(depth)["filename"]


def get_current_file_path(depth=2) -> Path:
    return frameinfo(depth)["path"]


def get_project_path(depth_current_file=1) -> str:
    """current file dir - depth """
    return frameinfo(1 + depth_current_file)["pathname"]


def abspath(path: str) -> Path:
    # if not is_file_exist(path):
    #     return None
    return Path(os.path.abspath(path))


def relpath(path: str) -> Path:
    # if not is_file_exist(path):
    #     return None
    return Path(os.path.relpath(path))


def recall_current_function(sleep_time):
    """ Be careful to not modify given function's args within the local context otherwise the call will be with thoses modified args """
    sleep(sleep_time)
    calling_frame = currentframe().f_back
    function = calling_frame.f_globals[calling_frame.f_code.co_name]
    arg_values = getargvalues(calling_frame)
    called_args = {arg_name: arg_values.locals[arg_name] for arg_name in arg_values[0]}
    return function(**called_args)


def frameinfo(backtimes=0, debug=False) -> Optional[dict]:
    frame = currentframe()
    try:
        for _ in range(backtimes):
            frame = frame.f_back
        pathname = frame.f_code.co_filename
    except AttributeError:
        # print("backtimes is too high")
        return None
    # fun_name = frame.f_code.co_name
    local_args = frame.f_locals
    line = frame.f_lineno
    function_name = frame.f_code.co_name
    sep = os.path.sep
    if pathname.find(os.path.sep) == -1:
        sep = "/"
    if debug:
        print("Current path:", pathname)
        # print("Current fun:", fun_name)
        print("Current fun args:", local_args)
        # print("Current line:", line)
        print(os.path.sep, pathname.rfind(sep))
        print(os.path.sep, pathname.rfind("."))
    try:
        pathname_complete = pathname
        filename = pathname[pathname.rindex(sep) + 1:pathname.rindex(".")]
        extension = pathname[pathname.rindex("."):]
        pathname = pathname[:pathname.rindex(sep) + 1]
    except ValueError:
        filename, pathname, extension, pathname_complete = ["debuging"] * 4
    if debug:
        print("Current file:", filename)
    # return {"filename": filename, "pathname": pathname, "fun_name": fun_name, "lineno": line, "local_args": local_args}
    return {
        "pathname_complete": pathname_complete,  # /path/file.ext
        "path": Path(pathname_complete),  # Path(/path/file.ext)
        "pathname": pathname,  # /path/
        "filename": filename,  # file
        "extension": extension,  # ext
        "line": line,
        "function_name": function_name,
        "local_args": local_args
    }


def print_line(extra=""):
    print(frameinfo(2)["line"], ":", extra)


def check_frames():
    for i in range(10):
        print(i, frameinfo(i + 1))
    return


# def current_file():
#     return inspect.currentframe().f_code.co_filename


def current_lines(start_depth=2, end_depth: Optional[int] = None):
    i = start_depth
    lst = []
    try:
        while end_depth is None or end_depth < i:
            frame = frameinfo(i)
            if frame is None:
                break
            lst.append(frame["filename"] + ":" + str(frame["line"]))
            i += 1
    except AttributeError:
        return lst
    return lst


def get_current_function_name():
    a = currentframe().f_back.f_code.co_name
    b = currentframe().f_back.f_code
    c = currentframe().f_back
    d = currentframe()
    return currentframe().f_back.f_code.co_name


def get_current_parameters():
    frame = currentframe().f_back
    locals = frame.f_locals
    args = frame.f_code.co_varnames
    args = args if args[0] != "self" else args[1:]
    return {arg: locals[arg] for arg in args if arg in locals}


# def frameinfo_stack(stack=0, debug=False):
#     """ ne fonctionne pas dans les threads"""
#     frame: FrameInfo = inspect.stack()[stack]
#     pathname = frame.filename
#     sep = os.path.sep
#     if pathname.find(os.path.sep) == -1:
#         sep = "/"
#     if debug:
#         print("Current path:", pathname)
#         print("Current fun:", frame.function)
#         print("Current line:", frame.lineno)
#         print(os.path.sep, pathname.rfind(sep))
#         print(os.path.sep, pathname.rfind("."))
#     filename = pathname[pathname.rindex(sep) + 1:pathname.rindex(".")]
#     if debug:
#         print("Current file:", filename)
#     return {"filename": filename, "pathname": pathname, "function": frame.function, "lineno": frame.lineno}

# def p(*args):
#     text = " ".join([str(arg) for arg in args])
#     print(inspect.stack()[1].lineno, text[:500], file=sys.stderr, flush=True)
#     pass


if __name__ == '__main__':
    # print(current_file())
    # print(current_lines())
    # print(current_infos())
    print(check_frames())
