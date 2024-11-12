import sys
import threading
import traceback
from threading import Thread
from time import sleep
from typing import Callable

# import Alert
from Files import is_file_exists, delete, run_file
from Introspection import check_frames, frameinfo

delete("locked")


def run(fun: Callable, arguments: dict = {}, wait_a_bit: float = 0.0, alert_if_error=True, print_if_error=True, name=None,
        daemon=False, ignore_error=False) -> threading:
    """
    run(playback.play, arguments={"audio_segment": sound})
    """

    def aux():
        if ignore_error:
            try:
                fun(**arguments)
            except Exception:
                if print_if_error:
                    print(traceback.format_exc(), file=sys.stderr)
                    print(name or fun.__name__, file=sys.stderr)
                # if alert_if_error:
                #     Alert.alert(str(name or fun.__name__) + "\n\n" + traceback.format_exc(), level=3)
        else:
            fun(**arguments)

    thread = Thread(target=aux, daemon=daemon)
    if name:
        thread.name = name
    elif getattr(fun, "__name__", None):
        thread.name = fun.__name__
    thread.start()
    sleep(wait_a_bit)
    return thread


def loop_run(fun: Callable, sleep_after_execution: float = 0.1, pre_sleep=0, **kwargs):
    def loop():
        sleep(pre_sleep)
        while True:
            if not is_file_exists(locker_name):
                # print("execution started")
                run(fun, 0.1, **kwargs)
            while is_file_exists(locker_name):
                sleep(0.001)
            # print("execution ended")
            sleep(sleep_after_execution)

    locker_name = "locked_" + fun.__name__
    delete(locker_name)
    run(loop)


def exit_n_rerun():
    old_frame = None
    i = 0
    while True:
        frame = frameinfo(i)
        if frame is None:
            break
        #     i += 1
        #     continue
        if frame["filename"] == "_pydev_execfile":
            break
        old_frame = frame
        i += 1
    file = old_frame["pathname_complete"]
    # file = r"B:\_Documents\Pycharm\Util\test.ahk"
    run_file(file)
    exit()


def rerun_if_stop(fun):
    while True:
        thread = run(fun)
        thread.join()


def get_current_thread():
    return threading.current_thread()
