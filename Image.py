""" import cv2 on Pycharm
Resolve all "Cannot find reference 'xxx' in '__init__.py' under Pycharm":
    (ctrl+click on cv2 copy the path into your clipboard)
    PyCharm -> Settings -> Project -> Python Interpreter -> Python Interpreter: or Gear symbol -> Show all ->
    tree folder -> +select the folder where the opencv package is located (ctrl+click on cv2) -> done
https://www.delftstack.com/howto/python/python-color-spectrums/
https://pyimagesearch.com/2021/01/19/opencv-bitwise-and-or-xor-and-not/
"""
import _pickle
import copy
import pickle
from random import randint
import sys
import threading
from time import sleep
import traceback
from typing import Callable, Optional, Union

import cv2 as cv
import matplotlib
from matplotlib import image as mpimg
import matplotlib as mpl
import matplotlib.pyplot as plt
from numpy import ndarray
# import mss.tools
# import pywhatkit
# from mss import ScreenShotError
import numpy as np
import pyqrcode
import pytesseract
from pyzbar.pyzbar import decode
from screeninfo import Monitor
import win32con
import win32gui
import win32ui

from Classes import Point, Rectangle
from Colors import printc
from Files import delete, is_ascii, is_file_exists, move_to, overwrite
import Threads
from Times import elapsed_seconds, now
from Util import COMMON_CHARS, restrict_num, string_encoded_to_bytes

input_path = 'input.png'
output_path = 'out.png'

# RGB config most of the time because matplotlib is RGB
EVENT_DICT = {}
RED_ISOLATION = (255, 100, 100)
GREEN_ISOLATION = (100, 255, 100)
BLUE_ISOLATION = (100, 100, 255)
LOCKER = False

pytesseract.pytesseract.tesseract_cmd = r'B:\Programmes\Tesseract-OCR\tesseract.exe'


def screenshot_fastest(x0: float, y0: float, x1: float, y1: float, dest="out.png", save_it=False, autoconvert=True) -> ndarray:
    global LOCKER
    while LOCKER:
        sleep(0.01)
    x0_, y0_, x1_, y1_ = map(int, (x0, y0, x1, y1))
    w = x1_ - x0_
    h = y1_ - y0_
    assert w > 0 and h > 0
    hwnd = None
    try:
        w_dc = win32gui.GetWindowDC(hwnd)
        dc_obj = win32ui.CreateDCFromHandle(w_dc)
        c_dc = dc_obj.CreateCompatibleDC()
        data_bit_map = win32ui.CreateBitmap()
        data_bit_map.CreateCompatibleBitmap(dc_obj, w, h)
        c_dc.SelectObject(data_bit_map)
        c_dc.BitBlt((0, 0), (w, h), dc_obj, (x0_, y0_), win32con.SRCCOPY)
        signed_ints_array = data_bit_map.GetBitmapBits(True)
        img = np.fromstring(signed_ints_array, dtype='uint8')
        img.shape = (h, w, 4)
        if autoconvert:
            img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        if save_it:
            data_bit_map.SaveBitmapFile(c_dc, dest)
        dc_obj.DeleteDC()
        c_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, w_dc)
        win32gui.DeleteObject(data_bit_map.GetHandle())
        LOCKER = False
        return img
    except win32ui.error:
        # print("err", file=sys.stderr)
        # print(traceback.format_exc(), file=sys.stderr)
        sleep(0.1)
        # Threads.exit_n_rerun()
        return screenshot_fastest(x0, y0, x1, y1, dest, save_it)
    # Threads.run(aux)


# def screenshot_mss(x0: float, y0: float, x1: float, y1: float, dest="out.png"):
#     x0, y0, x1, y1 = map(int, (x0, y0, x1, y1))
#     w = x1 - x0
#     h = y1 - y0
#     with mss.mss() as sct:
#         rect = {"left": x0, "top": y0, "width": w, "height": h}
#     try:
#         im = sct.grab(rect)
#         # mss.tools.to_png(im.rgb, im.size, output=dest)
#     except ScreenShotError:
#         pass


# def screenshot_boxcutter(x0: float, y0: float, x1: float, y1: float, dest="out.png"):
#     assert "png" not in dest
#     x0, y0, x1, y1 = map(int, (x0, y0, x1, y1))
#     options = "-c {},{},{},{} {}".format(x0, y0, x1, y1, dest)
#     os.system(r"A:\Programmes\AutoHotkey\Lib\boxcutter\boxcutter.exe " + options)


def screenshot_monitor(monitor: Monitor | Rectangle, display_scaling=100, dest="out.png", delay=0,
                       option="fastest", get_it=False) -> ndarray:
    x0, y0, w, h = monitor.x0, monitor.y0, monitor.w, monitor.h
    w, h = map(lambda x: x * display_scaling / 100, (w, h))
    screenshot = None
    if option == "fastest":
        screenshot = screenshot_fastest(x0, y0, x0 + w, y0 + h, dest, save_it=not get_it)
    # elif option == "boxcutter":
    #     screenshot_boxcutter(x0, y0, x0 + w, y0 + h, dest)
    # elif option == "mss":
    #     screenshot_mss(x0, y0, x0 + w, y0 + h, dest)
    sleep(delay)
    # if get_it:
        # image = read(dest)
        # return screenshot_monitor(monitor, display_scaling, dest, delay, option, get_it) if image is None else image
    return screenshot


def screenshot_loop(monitor: Monitor, display_scaling=100):
    def loop():
        screenshot_monitor(monitor, display_scaling, "live.png")
        overwrite("locked_loop", ".")
        # image = read("live.png")
        # check_auto = crop(image, 265, 78, 122, 45)
        # check_auto = filtering_color(check_auto, (125,) * 3, (255,) * 3, set_color_in=None)
        # save(check_auto, "auto.png")
        delete("locked_loop")

    Threads.loop_run(loop, sleep_after_execution=0.5)


def create_with_color(shape: tuple[int, int, int], rgb: tuple[int, int, int] = (0, 0, 0)) -> np.array:
    image = np.zeros(shape, np.uint8)
    image[:] = rgb
    return image


"""##### Image modifiers #####"""


def negative(image: np.array) -> np.array: return cv.bitwise_not(image)


# noinspection PyUnresolvedReferences
def grayscale(image: np.array) -> np.array: return cv.cvtColor(image, cv.COLOR_RGB2GRAY)


def median_blur(image: np.array) -> np.array: return cv.medianBlur(image, 5)


def dilate(image: np.array) -> np.array:
    kernel = np.ones((5, 5), np.uint8)
    return cv.dilate(image, kernel, iterations=1)


def erode(image: np.array) -> np.array:
    kernel = np.ones((5, 5), np.uint8)
    return cv.erode(image, kernel, iterations=1)


def morphology_ex(image: np.array) -> np.array:
    kernel = np.ones((5, 5), np.uint8)
    return cv.morphologyEx(image, cv.MORPH_OPEN, kernel)


def canny(image: np.array) -> np.array: return cv.Canny(image, 100, 200)


def match_template(image: np.array, template) -> np.array: return cv.matchTemplate(image, template, cv.TM_CCOEFF_NORMED)


MODIFIERS_FUNCTION = [lambda x: x, grayscale, median_blur, morphology_ex, erode, dilate, canny]


def isolate_img(image: np.array, rgb_min: tuple, rgb_max: tuple) -> np.array:
    # TODO transparent background
    # No hsv
    mask = cv.inRange(image, np.array(rgb_min), np.array(rgb_max))
    return cv.bitwise_and(image, image, mask=mask)


def filtering_intensity(image: np.array,
                        rgb_min: tuple[int, int, int],
                        rgb_max: tuple[int, int, int],
                        set_color_in=None,
                        set_color_out=None) -> np.array:
    a, b, c = rgb_min
    d, e, f = rgb_max
    filter_in = np.where(
        ((a <= image[:, :, 0]) & (image[:, :, 0] <= d)) |
        ((b <= image[:, :, 1]) & (image[:, :, 1] <= e)) |
        ((c <= image[:, :, 2]) & (image[:, :, 2] <= f))
    )
    filter_out = np.where(
        ((a > image[:, :, 0]) | (image[:, :, 0] > d)) &
        ((b > image[:, :, 1]) | (image[:, :, 1] > e)) &
        ((c > image[:, :, 2]) | (image[:, :, 2] > f))
    )
    new_image = copy.copy(image)
    if set_color_in is not None:
        new_image[filter_in] = set_color_in
    if set_color_out is not None:
        new_image[filter_out] = set_color_out
    return new_image


def filtering_color(image: np.array,
                    rgb_min: tuple[int, int, int],
                    rgb_max: tuple[int, int, int],
                    set_color_in: Optional[tuple[int, int, int]] = (255, 255, 255),
                    set_color_out: Optional[tuple[int, int, int]] = (0, 0, 0)) -> np.array:
    a, b, c = rgb_min
    d, e, f = rgb_max
    filter_in = np.where(
        ((a <= image[:, :, 0]) & (image[:, :, 0] <= d)) &
        ((b <= image[:, :, 1]) & (image[:, :, 1] <= e)) &
        ((c <= image[:, :, 2]) & (image[:, :, 2] <= f))
    )
    filter_out = np.where(
        ((a > image[:, :, 0]) | (image[:, :, 0] > d)) |
        ((b > image[:, :, 1]) | (image[:, :, 1] > e)) |
        ((c > image[:, :, 2]) | (image[:, :, 2] > f))
    )
    new_image = copy.copy(image)
    if set_color_in is not None:
        new_image[filter_in] = set_color_in
    if set_color_out is not None:
        new_image[filter_out] = set_color_out
    return cv.cvtColor(new_image, cv.COLOR_BGR2RGB)


def filter_pixels_with_intensity(image: np.array,
                                 rgb_min: tuple[int, int, int],
                                 rgb_max: tuple[int, int, int],
                                 variation = 0,
                                 set_color: tuple[int, int, int, int] = (0, 0, 0)) -> np.array:
    """ All pixel that are in range are not changed, other are set to black """
    return filtering_intensity(image, [p - variation for p in rgb_min], [p + variation for p in rgb_max], set_color_out=set_color)


def create_mask(image: np.array, rgb_min: tuple[int, int, int], rgb_max: tuple[int, int, int]) -> np.array:
    """ All pixel that are in range are set to white, other are set to black """
    return filtering_intensity(image, rgb_min, rgb_max, set_color_in=(255, 255, 255), set_color_out=(0, 0, 0))


def get_only_color(pixel, image: np.array, rgb_variation=(5, 5, 5)) -> np.array:
    rgb_isolation_min = tuple(max(0, pixel[i] - rgb_variation[i]) for i in range(len(pixel)))
    rgb_isolation_max = tuple(min(255, pixel[i] + rgb_variation[i]) for i in range(len(pixel)))
    return isolate_img(image, rgb_isolation_min, rgb_isolation_max)


def get_only_white(image: np.array, variation: int = 25) -> np.array:
    rgb_isolation_min = (255 - variation, 255 - variation, 255 - variation)
    rgb_isolation_max = (255, 255, 255)
    return isolate_img(image, rgb_isolation_min, rgb_isolation_max)


def get_only_black(image: np.array, variation: int = 25) -> np.array:
    """ return black color as white color """
    rgb_isolation_min = (0, 0, 0)
    rgb_isolation_max = (variation, variation, variation)
    mask = cv.inRange(image, np.array(rgb_isolation_min), np.array(rgb_isolation_max))
    image = create_with_color(image.shape, (255, 255, 255))
    return cv.bitwise_and(image, image, mask=mask)


def concat_black_n_white(image: np.array, variation: int = 25) -> np.array:
    return add(get_only_white(image, variation), get_only_black(image, variation))


def get_only_colored(image: np.array, variation=25) -> np.array:
    return cv.subtract(image, concat_black_n_white(image, variation))


def add(*args: np.array) -> np.array:
    result = args[0]
    for image in args[1:]:
        result = cv.add(result, image)
    return result


def sub(*args: np.array) -> np.array:
    result = args[0]
    for image in args[1:]:
        result = cv.absdiff(result, image)
    return result


"""########## OCR ############"""


def ocr(img: np.ndarray | str,
        config: str = r"--oem 3 --psm 6",
        # config: str = r"--oem 3 --psm 12",
        whitelist_ocr: str = COMMON_CHARS,
        blacklist_ocr: str = "",
        whitelist_filter: str = COMMON_CHARS,
        blacklist_filter: str = "",
        debug: bool = False) -> str:
    """ config="--oem 3 --psm {}".format(j) """
    # https://ai-facets.org/tesseract-ocr-best-practices/
    # --psm: 6, 7, 12
    if type(img) is str:
        img = read(img)
    config += " -c tessedit_char_whitelist={} -c tessedit_char_blacklist={}".format(whitelist_ocr, blacklist_ocr)
    img_to_str = pytesseract.image_to_string(img, config=config)
    img_to_str = "".join([char for char in img_to_str if char in whitelist_filter and char not in blacklist_filter])
    if len(img_to_str) and img_to_str[-1] == "\n":
        img_to_str = img_to_str[:-1]
    if debug:
        printc(img_to_str, background_color="black")
    return img_to_str


"""##### Image viewer #####"""


def reset_event_vars():
    global EVENT_DICT
    EVENT_DICT = {"i_event": 0, "next_i_event": 0, "i_display_images": 0, "arrays": {}, "x": 0, "y": 0, "ocr": False,
                  "original_img": False, "exit_display": False, "delete": False, "save": False, "time": now()}


reset_event_vars()


def events(event):
    global EVENT_DICT
    printc(event.key, background_color="blue")
    space = " "
    if (event.key not in ["q", "s", "left", "right", "up", "down", "enter", "+", "-", ".", "delete", space] + list(
            map(str, range(10)))
            or elapsed_seconds(EVENT_DICT["time"]) < 0.1):
        return
    EVENT_DICT["i_event"] += 1
    EVENT_DICT["next_i_event"] = EVENT_DICT["i_event"]
    len_images = len(EVENT_DICT["arrays"])
    if event.key == "q":
        plt.close("all")
        EVENT_DICT["exit_display"] = True
    if event.key == "s":
        EVENT_DICT["save"] = True
    elif event.key == "left":
        # EVENT_DICT["i_display_images"] = (EVENT_DICT["i_display_images"] - 1) % len_images
        if EVENT_DICT["."]:
            EVENT_DICT["i_display_images"] = EVENT_DICT["i_display_images"] - 1
        EVENT_DICT["i_display_images"] = EVENT_DICT["i_display_images"] - 1
    elif event.key == "right":
        # EVENT_DICT["i_display_images"] = (EVENT_DICT["i_display_images"] + 1) % len_images
        if EVENT_DICT["."]:
            EVENT_DICT["i_display_images"] = EVENT_DICT["i_display_images"] - 1
        EVENT_DICT["i_display_images"] = EVENT_DICT["i_display_images"] + 1
    elif event.key == "up":
        EVENT_DICT["x"] += 1
    elif event.key == "down":
        EVENT_DICT["x"] -= 1
    elif event.key == "+":
        EVENT_DICT["y"] += 1
    elif event.key == "-":
        EVENT_DICT["y"] -= 1
    elif event.key == ".":
        EVENT_DICT["."] = not EVENT_DICT["."]
    elif event.key == "enter":
        EVENT_DICT["ocr"] = not EVENT_DICT["ocr"]
    elif event.key == "delete":
        EVENT_DICT["delete"] = True
    elif event.key == space:
        EVENT_DICT["original_img"] = not EVENT_DICT["original_img"]
    elif event.key in map(str, range(10)):
        EVENT_DICT["i_display_images"] = int(event.key) % len_images
    EVENT_DICT["time"] = now()
    print(EVENT_DICT["i_display_images"], "ocr", EVENT_DICT["ocr"], "original", EVENT_DICT["original_img"], "\n")


def init_image_viewer_white(full_screen: bool = False, title="") -> matplotlib.pyplot:
    from matplotlib import pyplot as plt
    # plt.rcParams['toolbar'] = 'None'
    plt.rcParams["keymap.zoom"].append("a")
    plt.rcParams["keymap.back"].append("²")
    plt.rcParams["keymap.save"] = ""
    plt.rcParams['figure.figsize'] = (10, 6)
    if threading.current_thread() == threading.main_thread():
        mpl.use('Qt5Agg')  # pip install PyQt5
    # curve_color = "#0F1623"
    # plt.rcParams['axes.facecolor'] = curve_color
    # fig.patch.set_facecolor(curve_color)
    fig: plt.figure = plt.figure()
    # ax = fig.add_axes([0, 0, 0, 0])
    ax = fig.axes
    fig.canvas.mpl_connect('key_press_event', events)
    if full_screen:
        fig.canvas.manager.full_screen_toggle()
    # plt.ion()
    plt.title(title)
    return plt, ax, fig


def init_image_viewer_dark(full_screen: bool = False, figsize=(16, 9), curve_color=None, title="") -> tuple[
    matplotlib.pyplot, matplotlib.figure.Axes, matplotlib.figure.Figure]:
    from matplotlib import pyplot as plt
    # plt.rcParams['toolbar'] = 'None'
    plt.rcParams["keymap.zoom"].append("a")
    plt.rcParams["keymap.back"].append("²")
    plt.rcParams["keymap.save"] = ""
    plt.rcParams['figure.figsize'] = figsize
    if threading.current_thread() == threading.main_thread():
        mpl.use('Qt5Agg')  # pip install PyQt5
    if curve_color is None:
        curve_color = "#0F1623"
    plt.rcParams['axes.facecolor'] = curve_color
    plt.rcParams['axes.edgecolor'] = 'white'
    plt.rcParams['axes.labelcolor'] = 'white'
    fig, ax = plt.subplots()
    # fig: plt.figure = plt.figure()
    fig.patch.set_facecolor(curve_color)
    # ax = fig.axes()
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    # ax = fig.add_axes([0, 0, 1, 1])
    fig.canvas.mpl_connect('key_press_event', events)
    if full_screen:
        fig.canvas.manager.full_screen_toggle()
    # plt.ion()
    # plt.show()
    plt.title(title)
    return plt, ax, fig


def init_plt(full_screen: bool = False, figsize=(16, 9), curve_color="#0F1623", title="") -> tuple[
    matplotlib.pyplot, matplotlib.figure.Axes, matplotlib.figure.Figure]:
    from matplotlib import pyplot as plt
    if threading.current_thread() == threading.main_thread():
        mpl.use('Qt5Agg')  # pip install PyQt5
    plt.rcParams["keymap.zoom"].append("a")
    plt.rcParams["keymap.back"].append("²")
    plt.rcParams["keymap.save"] = ""
    # plt.rcParams['toolbar'] = 'None'
    plt.rcParams["figure.figsize"] = figsize
    plt.rcParams["axes.facecolor"] = curve_color
    plt.rcParams["axes.edgecolor"] = "white"
    plt.rcParams["axes.labelcolor"] = "white"
    plt.rcParams["axes.titlecolor"] = "white"
    fig, ax = plt.subplots()
    fig.patch.set_facecolor(curve_color)
    fig.canvas.mpl_connect('key_press_event', events)
    if full_screen:
        fig.canvas.manager.full_screen_toggle()
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    # fig: plt.figure = plt.figure()
    # ax = fig.axes()
    # ax = fig.add_axes([0, 1, 0, 0])
    # plt.ion()
    # plt.show()
    ax.xaxis.set_minor_locator(plt.NullLocator())
    plt.title(title)
    return plt, ax, fig

def get_black_or_white_or_isolate(image: np.array,
                                  rgb_min: tuple[int, int, int],
                                  rgb_max: tuple[int, int, int], ) -> np.array:
    if rgb_min == (0, 0, 0):
        image = get_only_black(image)
    elif rgb_max == (255, 255, 255):
        image = get_only_white(image)
    else:
        image = isolate_img(image, rgb_min, rgb_max)
    return image


def read(image_path: str, gray=False, to_rgb=False) -> np.array:
    try:
        if gray:
            return cv.imread(image_path, 0)
        if not is_ascii(image_path):
            return mpimg.imread(image_path)
        if to_rgb:
            return cv.cvtColor(cv.imread(image_path), cv.COLOR_BGR2RGB)
        return cv.imread(image_path)
        # return mpimg.imread(image_path)
    except cv.error:
        # print("err, image may no exist", image_path)
        return None


def fill_images_array(images: list[np.array] | list[str],
                      rgb_min: Optional[tuple[int, int, int]] = None,
                      rgb_max: Optional[tuple[int, int, int]] = None) -> dict[str, np.array]:
    EVENT_DICT["arrays"] = {}
    for i in range(len(images)):
        image = images[i]
        if type(image) is str:
            EVENT_DICT["arrays"][image] = None
        else:
            # image_np = cv.cvtColor(image, cv.COLOR_BGR2RGB)
            # if rgb_min is not None and rgb_max is not None:
            #     image_np = get_black_or_white_or_isolate(image, rgb_min, rgb_max)
            EVENT_DICT["arrays"][str(i)] = image
            # EVENT_DICT["arrays"][str(i)] = None
    return EVENT_DICT["arrays"]


def retire_black_bar(np_image: ndarray):
    x0 = None
    x1 = None
    for nd_array in np_image:
        if nd_array.max() == 0:
            continue
        i = next(x[0] for x in enumerate(nd_array) if (0, 0, 0) not in x[1])
        j = next(x[0] for x in enumerate(nd_array[::-1]) if (0, 0, 0) not in x[1])
        x0 = min(x0 if x0 else i, i)
        x1 = min(x1 if x1 else i, j)
    w = np_image.shape[1]
    new_shape = (np_image.shape[0], w - x0 - x1, np_image.shape[2])
    image = np.zeros(new_shape, np.uint8)
    for i in range(len(np_image)):
        image[i] = np_image[i][x0:w - x1]
    return image


def display_images(images: list[np.ndarray] | np.ndarray | str | list[str],
                   full_screen: bool = False,
                   to_rgb: bool = False,
                   autorun: float = 0,
                   mapping=None):
    import matplotlib.pyplot as plt

    if type(images) is not list:
        images = [images]
    EVENT_DICT["."] = autorun > 0
    fill_images_array(images)
    plt, ax, fig = init_image_viewer(plt, full_screen)
    while not EVENT_DICT["exit_display"]:
        i = EVENT_DICT["i_display_images"] % len(images)
        print(i, len(EVENT_DICT["arrays"]), images[i])
        if str(i) in EVENT_DICT["arrays"]:
            if EVENT_DICT["arrays"][str(i)] is None:
                EVENT_DICT["arrays"][str(i)] = read(images[i], to_rgb=to_rgb)
            display_image = EVENT_DICT["arrays"][str(i)]
        elif type(images[i]) is str and images[i] in EVENT_DICT["arrays"]:
            if EVENT_DICT["arrays"][images[i]] is None:
                EVENT_DICT["arrays"][images[i]] = read(images[i], to_rgb=to_rgb)
            display_image = EVENT_DICT["arrays"][images[i]]
        else:
            display_image = EVENT_DICT["arrays"][str(i)]
        if mapping is not None:
            display_image = mapping(display_image)
        if autorun > 0 and EVENT_DICT["."]:
            plt.cla()
            # noinspection PyUnboundLocalVariable
            plt.imshow(display_image)
            start = now()
            i_event = EVENT_DICT["i_event"]
            while autorun - elapsed_seconds(start) > 0 and EVENT_DICT["i_event"] == i_event:
                fig.canvas.start_event_loop(0.01)
            if EVENT_DICT["."]:
                EVENT_DICT["i_display_images"] = (EVENT_DICT["i_display_images"] + 1) % len(images)
            plt.cla()
            plt.imshow(display_image)
        else:
            new_action = EVENT_DICT["i_event"] == EVENT_DICT["next_i_event"]
            if new_action:
                plt.cla()
                plt.imshow(display_image)
            i_event = EVENT_DICT["i_event"]
            start = now()
            while 0.2 - elapsed_seconds(start) > 0 and EVENT_DICT["i_event"] == i_event:
                fig.canvas.start_event_loop(0.01)
            if new_action:
                EVENT_DICT["next_i_event"] += 1
                plt.cla()
                plt.imshow(display_image)
        if EVENT_DICT["delete"]:
            EVENT_DICT["delete"] = False
            try:
                move_to(images[i],
                        "C:\\Users\\Alexis\\Pictures\\Nouveau dossier\\trash\\" + images[i][images[i].rfind("\\") + 1:])
            except FileNotFoundError:
                pass
        if EVENT_DICT["save"]:
            EVENT_DICT["save"] = False
            image_name = images[i]
            if type(image_name) is not str:
                file_name = "Images\\out.png"
            else:
                ext = images[i].rfind(".")
                file_name = "C:\\Users\\Alexis\\Pictures\\Nouveau dossier\\" + images[i][
                                                                               images[i].rfind("\\") + 1:ext] + "_" + \
                            images[i][ext:]
            plt.savefig(file_name, bbox_inches=0, pad_inches=0.1)
            save(retire_black_bar(read(file_name)), file_name)
    reset_event_vars()
    plt.close()


def display_images_n_debug(images: list[np.ndarray] | np.ndarray,
                           full_screen: bool = False,
                           ocr: bool = False,
                           autorun: float = 0,
                           rgb_min: Optional[tuple[int, int, int]] = None,
                           rgb_max: Optional[tuple[int, int, int]] | int = None,
                           variation: Optional[int] = None) -> list[np.ndarray]:
    import matplotlib.pyplot as plt

    if type(images) is not list:
        images = [images]
    assert (rgb_min is None) is (rgb_max is None) or ((rgb_min or rgb_max) and variation)
    EVENT_DICT["ocr"] = ocr
    EVENT_DICT["."] = autorun > 0
    fill_images_array(images, rgb_min, rgb_max)
    plt, ax, fig = init_image_viewer(plt, full_screen)
    while not EVENT_DICT["exit_display"]:
        i = EVENT_DICT["i_display_images"]
        new_action = EVENT_DICT["i_event"] == EVENT_DICT["next_i_event"]
        if new_action or EVENT_DICT["."]:
            display_image = images[i]
            if rgb_min is not None and (rgb_max is not None or variation is not None):
                if variation:
                    rgb_isolation_min = tuple(
                        map(lambda x: int(restrict_num(x - variation + EVENT_DICT["y"], 0, 255)), rgb_min))
                    rgb_isolation_max = tuple(
                        map(lambda x: int(restrict_num(x + variation + EVENT_DICT["x"], 0, 255)), rgb_min))
                else:
                    rgb_isolation_min = tuple(map(lambda x: int(restrict_num(x + EVENT_DICT["y"], 0, 255)), rgb_min))
                    rgb_isolation_max = tuple(map(lambda x: int(restrict_num(x + EVENT_DICT["x"], 0, 255)), rgb_max))
                print(rgb_isolation_min)
                print(rgb_isolation_max)
                only_black = rgb_isolation_min == (0, 0, 0)
                only_white = rgb_isolation_max == (255, 255, 255)
                if not only_black and not only_white and rgb_isolation_min and rgb_isolation_max:
                    display_image = isolate_img(display_image, rgb_isolation_min, rgb_isolation_max)
                if only_black and only_white:
                    display_image = concat_black_n_white(display_image)
                elif only_black:
                    display_image = get_only_black(display_image)
                elif only_white:
                    display_image = get_only_white(display_image)
            if EVENT_DICT["ocr"]:
                ocr(display_image)
            EVENT_DICT["arrays"][i] = display_image
            EVENT_DICT["next_i_event"] += 1
            if EVENT_DICT["original_img"]:
                display_image = images[i]
            else:
                display_image = EVENT_DICT["arrays"][i]
            plt.cla()
            plt.imshow(display_image)
        if autorun > 0:
            fig.canvas.start_event_loop(autorun)
            if EVENT_DICT["."]:
                EVENT_DICT["i_display_images"] = (EVENT_DICT["i_display_images"] + 1) % len(images)
        else:
            print("c")
            fig.canvas.start_event_loop(0.2)
    plt.close()
    images = EVENT_DICT["arrays"]
    reset_event_vars()
    return images


def image_modifier(image,
                   functions: list[Callable[[np.array], np.array]] = None,
                   rgb_isolation_min: Optional[tuple[int, int, int]] = None,
                   rgb_isolation_max: Optional[tuple[int, int, int]] = None,
                   variation: Optional[int] = None,
                   rgb_min: tuple[int, int, int] = (0, 0, 0),
                   rgb_max: tuple[int, int, int] = (255, 255, 255)) -> list[np.ndarray]:
    if functions is not None:
        for function in functions:
            image = function(image)
    if rgb_isolation_min is not None:
        if variation is not None:
            rgb_isolation_max = rgb_isolation_min
            rgb_isolation_min = tuple(map(lambda x: int(restrict_num(x - variation, 0, 255)), rgb_isolation_min))
            rgb_isolation_max = tuple(map(lambda x: int(restrict_num(x + variation, 0, 255)), rgb_isolation_max))
        image = get_black_or_white_or_isolate(image, rgb_isolation_min, rgb_isolation_max)
    image = filter_pixels_with_intensity(image, rgb_min, rgb_max)
    return image


def save(img: np.ndarray, dest: str = "out.png", quality: int = 100):
    """ flags: https://docs.opencv.org/4.0.1/d4/da8/group__imgcodecs.html#ga292d81be8d76901bff7988d18d2b42ac"""
    # cv.imwrite(dest, img, [cv.IMWRITE_png_QUALITY, quality])
    cv.imwrite(dest, img)


# def image_to_ascii_art(file_name: str, dest: str = "out"):
#     """ Don't put add .txt extension on the dest name"""
#     pywhatkit.image_to_ascii_art(file_name, dest)


def create_qrcode(data: str | object, dest="out", scale=5) -> bool:
    if type(data) is not str:
        data = pickle.dumps(data)
    try:
        qrcode = pyqrcode.create(data, encoding="unicode_escape")  # utf-8 isn't working
    except ValueError:
        print(traceback.format_exc(), file=sys.stderr)
        printc("The data is too big to be stored through a QRCode", background_color="red")
        return False
    qrcode.png("images/{}.png".format(dest), scale=scale)
    qrcode.svg("images/{}.svg".format(dest), scale=scale)
    return True


def decode_qrcode(file_name="out.png"):
    # TODO svg to png
    assert ".svg" not in file_name, "convert svg to another format"
    # import cairosvg
    # cairosvg.svg2pdf(url='image.svg', write_to='image.pdf')
    qrcode = cv.imread(file_name)
    qrdecode = decode(qrcode)[0]  # utf-8 encoding, cannot change
    text_utf8 = qrdecode.data
    str_encoded_raw = text_utf8.decode(encoding='utf-8')
    text_unicode_escape = string_encoded_to_bytes(str_encoded_raw)
    try:
        value = pickle.loads(text_unicode_escape, encoding='unicode_escape')
    except _pickle.UnpicklingError:
        value = str_encoded_raw
    return value


def crop(image: np.array, x0: int | Rectangle, y0=None, w=None, h=None):
    img = copy.deepcopy(image)
    if type(x0) is Rectangle:
        h = x0.h
        w = x0.w
        y0 = x0.y0
        x0 = x0.x0
    if w == 0 or h == 0:
        return img
    return img[y0:y0 + h, x0:x0 + w]


def draw_rectangle(image: np.array, p0: tuple[int, int] | Point, p1: tuple[int, int] | Point, color=(0, 0, 255),
                   thickness=1):
    """ cv.rectangle is side effect, encapsulate to cancel the effect """
    return_image = copy.deepcopy(image)
    return cv.rectangle(return_image, p0, p1, color, thickness)


def image_search(image: Union[np.array, Rectangle],
                 templates: str | list[str] | list[tuple[str, Rectangle]],
                 confidence_min=90,
                 image_origin_on_screen=Point(0, 0),
                 display_scaling=100, delay=0, error_if_not_existing=False,
                 debug=False, pixel_mode=()) -> tuple[None, None] | tuple[Point, str]:
    """ https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html
        https://github.com/ClarityCoders/ComputerVision-OpenCV/blob/master/Lesson3-TemplateMatching/PlayGame.py
     """
    assert len(templates) != 0
    temp_name = "temp_image_search_%s.png" % str(randint(0, 100))
    if type(templates) is str:
        templates = [templates]
    if type(templates[0]) is str:
        templates = list(map(lambda x: (x, Rectangle(0, 0, 0, 0)), templates))
    base_top_left = None
    capture_image = image
    top_left = (0, 0)
    if type(image) is Rectangle:
        base_top_left = image
        capture_pixels = image.move_origin(image_origin_on_screen)
        if not pixel_mode:
            capture_pixels = capture_pixels.move_corners(1)
        # capture_image = None
        # while capture_image is None:
        capture_image = screenshot_monitor(capture_pixels, display_scaling, temp_name, delay=delay, get_it=True)
            # sleep(0.2) if capture_image is None else ""
        # image_origin_on_screen = image_origin_on_screen.top_left
    confidence = 0
    pixels_unfounded = 1
    for i, (folder_image, crop_size) in enumerate(templates):
        if not is_file_exists(folder_image):
            if debug:
                print("folder_image not exists")
            return None, None
        capture_image = crop(capture_image, crop_size)
        # folder_image = read(folder_image)
        folder_image = read(folder_image, gray=True)
        # display_images(capture_image)
        if pixel_mode:
            pixels_unfounded = np.count_nonzero(np.all(get_only_color(folder_image[0][0],
                                                                      capture_image, pixel_mode[i]) == [0, 0, 0],
                                                       axis=-1))
            if debug:
                printc("{} {}".format(pixels_unfounded, templates[i][0]),
                       color="green" if pixels_unfounded == 0 else "red")
            if pixels_unfounded == 0:
                break
        else:
            if debug:
                save(capture_image, dest="capture_image_temp.png")
                save(folder_image, dest="folder_image_temp.png")
            # if any error try to convert the image : cv.cvtColor(img, cv.COLOR_BGR2RGB)
            match = cv.matchTemplate(capture_image, folder_image, cv.TM_CCOEFF_NORMED)
            _, confidence, _, top_left = cv.minMaxLoc(match)
            confidence = round(confidence * 100, 3)
            if debug:
                printc("{} {}".format(confidence, templates[i][0]),
                       color="green" if confidence >= confidence_min else "red")
            if confidence >= confidence_min:
                break
    # if is_existing(temp_name):
    #     delete(temp_name)
    if (not pixel_mode and confidence < confidence_min) or (pixel_mode and pixels_unfounded > 0):
        return None, None
    # display_images(image)
    if len(folder_image.shape) == 2:
        h, w = folder_image.shape
        hh, ww = capture_image.shape
    else:
        h, w, _ = folder_image.shape
        hh, ww, _ = capture_image.shape
    uncrop_top_left = tuple(crop_size.top_left + Point(top_left))
    uncrop_bot_right = tuple(Point(uncrop_top_left[0] + w + 1, uncrop_top_left[1] + h + 1))
    if debug:
        image_debug = draw_rectangle(capture_image, uncrop_top_left, uncrop_bot_right)
        save(image_debug, "image_search_debug.png")
    if base_top_left:
        uncrop_top_left = Point(uncrop_top_left) + base_top_left.top_left
    return image_origin_on_screen + Point(uncrop_top_left) / (display_scaling / 100), templates[i][0]


def _test_funs():
    # create_qrcode({"ee": 56, (1, 2, 3): "486"})
    # print(decode_qrcode("images/out.png"))

    image_files = ["images/words1.png"]
    images = list(map(lambda x: read(x, to_rgb=True), image_files))

    image = images[0]
    # by color
    white_filter = get_only_white(image)
    yellow_filter = image_modifier(image, rgb_isolation_min=(0xFE, 0xC2, 0x00), variation=20)
    # yellow_filter = image_modifier(image, rgb_min=(0xFE, 0xC2, 0x00), variation=20)
    result = add(white_filter, yellow_filter)
    display_images(image)
    # ocr(result)

    # # by intensity
    high_colors = filter_pixels_with_intensity(image, rgb_min=(240, 240, 240), rgb_max=(255, 255, 255))
    display_images(high_colors)
    # image = get_only_white(image, variation=20)
    # save(image, "txt.png")
    ocr(high_colors)

    colored_filter = get_only_colored(image)
    display_images([image, colored_filter, sub(image, colored_filter)])


if __name__ == '__main__':
    _test_funs()
    # image_files = get_files_from_path(get_current_path() + "\\images\\", recursive=True)
    # display_images(image_files)
    display_images(["images/out.png"])
    exit()
