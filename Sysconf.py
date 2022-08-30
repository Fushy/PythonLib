from screeninfo import get_monitors, Monitor


def monitor_1080p(x, y):
    return Monitor(
        x=x,
        y=y,
        width=1920,
        height=1080,
        name="hide",
        is_primary=False,
    )


def screen_rect(x):
    return monitor_1080p((x_start_offset + x) / ratio, x / ratio)


MONITORS = get_monitors()
SCREENS = dict(zip(range(1, len(MONITORS) + 1), sorted(MONITORS, key=lambda m: (abs(m.x), abs(m.y)))))
FULL_SIZE = [min((monitor.x for monitor in MONITORS)),
             min((monitor.y for monitor in MONITORS)),
             max((monitor.x + monitor.width for monitor in MONITORS)),
             max((monitor.y + monitor.height for monitor in MONITORS))]
is_4k, is_QHD = False, False
ratio = 1
x_start_offset = 0
native_width = None
native_height = None
for monitor in MONITORS:
    if not monitor.is_primary:
        continue
    is_4k = monitor.width == 3840 and monitor.height == 2160
    is_QHD = monitor.width == 2560 and monitor.height == 1440
    is_1080 = monitor.width == 1920 and monitor.height == 1080
    native_width = monitor.width
    native_height = monitor.height
if is_4k:
    ratio = 1.5
    x_start_offset = -11
if is_QHD:
    ratio = 1
    x_start_offset = -7

SCREENS["hide"] = monitor_1080p(0, FULL_SIZE[3] + 100)
SCREENS["semi_hide_move"] = monitor_1080p(0, FULL_SIZE[3] - FULL_SIZE[3] * 0.1)
SCREENS["semi_hide"] = monitor_1080p(0, FULL_SIZE[3] - FULL_SIZE[3] * 0.05)
for name in SCREENS:
    SCREENS[name].x = SCREENS[name].x / ratio + x_start_offset
    SCREENS[name].y = SCREENS[name].y / ratio

# print(MONITORS)
# print(FULL_SIZE)
# print(SCREENS)
