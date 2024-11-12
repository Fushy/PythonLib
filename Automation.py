from asyncio import sleep
import os

import pyautogui
import win32gui
import pygetwindow as gw
from Classes import Point
from Files import is_file_exists


def launch_ahk_text(text, base=None, file_name="temp.ahk", encoding="utf8", reset_file=True):
    """ AutoHotkey.exe as administrator"""
    if is_file_exists(file_name) and not reset_file:
        os.system(file_name)
        return
    if base is None:
        base = """
                if not A_IsAdmin
                  Run *RunAs "%A_ScriptFullPath%"
                if not A_IsAdmin
                  ExitApp
                CoordMode, Pixel, Screen
                CoordMode, Mouse, Screen
                CoordMode, ToolTip, Screen
                SetTitleMatchMode, 1
                SetBatchLines, -1
                SetKeyDelay, 10
                DetectHiddenWindows, On
                """
    ahk_text = base + text
    try:
        with open(file_name, 'w', encoding=encoding) as f:
            f.write(ahk_text)
    except PermissionError:
        sleep(0.1)
        return launch_ahk_text(text, base, file_name, encoding, reset_file)
    os.system(file_name)


def click(x: int | Point | None = None, y=None, ahk=False, file_name="click.ahk"):
    if type(x) is Point:
        y = x.y
        x = x.x
    if not ahk:
        if x is None:
            pyautogui.click()
            return
        pyautogui.click(x=x, y=y)
    else:
        launch_ahk_text("""
        lParam := {}
        SendMessage, 0x201, 0x00000000, lParam,, A
        SendMessage, 0x202, 0x00000000, lParam,, A""".format(0 if x is None else (y << 16) | x), file_name=file_name)


def mouse_move(x: int | Point, y=None, ahk=False, title="A", file_name="mouse_move_vars.ahk"):
    if type(x) is Point:
        y = x.y
        x = x.x
    if not ahk:
        pyautogui.moveTo(x=x, y=y)
    else:
        launch_ahk_text("""
        winactivate, Program Manager
        mousegetpos, mx, my
        tooltip, a, mx-10, my-10
        mousemove, {}, {}, 0
        tooltip
        winactivate, {}""".format(x, y, title), file_name=file_name)


def mouse_click_ahk(x, y, title="A", file_name="mouse_click_ahk.ahk"):
    launch_ahk_text("""
        winactivate, Program Manager
        mousegetpos, mx, my
        tooltip, a, mx-10, my-10
        mousemove, {}, {}, 0
        tooltip
        winactivate, {}
        SendMessage, 0x201,,,, A
        SendMessage, 0x202,,,, A
        winactivate, Program Manager
        mousegetpos, mxx, myy
        tooltip, a, mxx-10, myy-10
        mousemove, mx, my, 0
        tooltip
        winactivate, {}""".format(x, y, title, title), file_name=file_name)


def click_n_rewind(x: int | Point | None, y=None):
    save_pos = mouse_get_pos()
    # move(x, y)
    click(x, y)
    mouse_move(save_pos)


def first_alpha_index(s):
    is_in = """!+"#"""
    start = False
    for i in range(len(s)):
        if not start and s[i] not in is_in:
            start = True
        elif start and s[i] not in is_in:
            return i - 1
    return 0


def send(keys_str: list, press_time=0, ahk=False):
    """ https://pyautogui.readthedocs.io/en/latest/keyboard.html#keyboard-keys
    send(["ctrl alt x"]) """
    if not ahk:
        for keys in keys_str:
            for key in keys.split():
                pyautogui.keyDown(key)
            # sleep(press_time)
            for key in keys.split():
                pyautogui.keyUp(key)
    elif ahk:
        # for key in keys:
        #     launch_ahk_text("""
        #     SendMessage, 0x0102, {}, 0x01f0010f,,A ; Char
        #     SendMessage, 0x0100, {}, 0x01f0010f,,A ; Down
        #     sleep, {}
        #     SendMessage, 0x0101, {}, 0x01f0010f,,A ; Up""".format(ord(key), ord(key), press_time, ord(key)))
        i = first_alpha_index(keys) + 1
        modifiers = keys[:i]
        keys = keys[i:]
        launch_ahk_text("""sendevent, {}[[{}]]""".format(modifiers, keys).replace("[[", "{").replace("]]", "}"), base="")


def mouse_get_pos() -> Point:
    flags, hcursor, (x, y) = win32gui.GetCursorInfo()
    return Point(x, y)


def win_get_active_title() -> str:
    return win32gui.GetWindowText(win32gui.GetForegroundWindow())


def get_all_windows_opened():
    return {title for title in gw.getAllTitles() if title}


def get_window(title):
    return next((t for t in get_all_windows_opened() if title in t), None)


def is_open_window(title):
    return any(title == t for t in get_all_windows_opened())


def win_get_pos(title):
    """ todo exe with ahk """
    instance = get_window(title)
    window_handle = win32gui.FindWindow(None, instance)
    if window_handle is None:
        return
    left, top, right, bottom = win32gui.GetWindowRect(window_handle)
    return left, top, right, bottom


if __name__ == '__main__':
    pass
