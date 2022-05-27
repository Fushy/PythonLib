import inspect
from datetime import datetime, timedelta
from typing import Callable

TIMEDELTA_ZERO = timedelta(seconds=0)


def now(utc=False, offset_h=0, offset_m=0, offset_s=0) -> datetime:
    offset = timedelta(hours=offset_h, minutes=offset_m, seconds=offset_s)
    return offset + (datetime.utcnow() if utc else datetime.now())


def to_timestamp(date_time: datetime) -> float:
    try:
        return date_time.timestamp()
    except AttributeError:
        return to_timestamp(to_datetime(date_time))


def to_datetime(obj, format: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    try:
        return datetime.fromtimestamp(int(obj))
    except TypeError:
        return datetime.strptime(str(obj), format.replace("/", "-"))
    except ValueError:
        return datetime.strptime(str(obj), format.replace("/", "-"))


def elapsed_timedelta(date_time: datetime):
    return datetime.now() - date_time


def elapsed_seconds(date_time: datetime):
    return (datetime.now() - date_time).total_seconds()


def elapsed_minutes(date_time: datetime):
    return (datetime.now() - date_time).total_seconds() / 60


def time_it(fun: Callable, *args):
    repeat_call_min = 10
    sec_elapsed_min = 1
    total_repeat = 5
    times_estimate = []
    start = now()
    i = 0
    while elapsed_seconds(start) < sec_elapsed_min or i < repeat_call_min:
        fun() if len(args) == 0 else fun(*args)
        i += 1
        if elapsed_seconds(start) <= sec_elapsed_min:
            repeat_call_min += 1
    for _ in range(total_repeat):
        for _ in range(int(repeat_call_min / 10)):
            fun() if len(args) == 0 else fun(*args)
        start = now()
        for i in range(repeat_call_min):
            fun() if len(args) == 0 else fun(*args)
        times_estimate.append(elapsed_seconds(start) / repeat_call_min)
    print(
        fun.__name__, round(sum(times_estimate) / len(times_estimate) * 1000, 3), "ms",
        len(times_estimate) * total_repeat, "times")
    return round(sum(times_estimate) / len(times_estimate) * 1000, 3)


def times_n(fun: Callable, n=100, *args):
    start = now()
    for i in range(n):
        fun(*args)
    print(inspect.currentframe().f_code.co_name, fun.__name__, round(elapsed_seconds(start) / n * 1000, 3), "ms")

# def test(browser, xpath):
#     # test 78.5 ms 25 times
#     return browser.get_element(xpath)
# def test(browser, xpath):
#     # test 136.6 ms 25 times
#     return browser.get_element(xpath).text
# def test(browser, xpath):
#     # test 103.839 ms 25 times
#     return get_element_text(browser.get_element(xpath))
# def test(browser, xpath):
#     # test 102.495 ms 25 times
#     return browser.get_text("", xpath)
