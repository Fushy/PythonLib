import threading
from hashlib import blake2b
from math import log
import os
from pathlib import Path
import sys
from time import sleep
import traceback

from gtts import gTTS
from peewee import CharField, CompositeKey, DateTimeField, Model, MySQLDatabase, Proxy, SqliteDatabase
from pydub import AudioSegment, playback

import Classes
from Files import delete, is_file_exists, run_file
from Introspection import frameinfo
import Telegrams
import Threads
from Times import elapsed_seconds, now


def db_to_float(db, using_amplitude=True):
    """
    Converts the input db to a float, which represents the equivalent
    ratio in power.
    """
    db = float(db)
    if using_amplitude:
        return 10 ** (db / 20)
    else:  # using power
        return 10 ** (db / 10)


def ratio_to_db(ratio, val2=None, using_amplitude=True):
    """
    Converts the input float to db, which represents the equivalent
    to the ratio in power represented by the multiplier passed in.
    """
    ratio = float(ratio)
    # accept 2 values and use the ratio of val1 to val2
    if val2 is not None:
        ratio = ratio / val2
    # special case for multiply-by-zero (convert to silence)
    if ratio == 0:
        return -float('inf')
    if using_amplitude:
        return 20 * log(ratio, 10)
    else:  # using power
        return 10 * log(ratio, 10)


def little_sound(duration_seconds=0.4, volume=0.1):
    sound = say("Hello world !", speed=2, just_create_file=True, debug=False)
    sound = cut_sound(sound, cut_percent=40)
    sound = change_volume(sound, volume)
    sound = change_duration(sound, duration_seconds)
    play_sound(sound)


def err_sound():
    sound = say("err", just_create_file=True)
    play_sound(cut_sound(sound, cut_percent=49) * 50, blocking=True)


def cut_sound(sound: str | AudioSegment, cut_percent) -> AudioSegment:
    if type(sound) is str:
        sound = AudioSegment.from_mp3(sound)
    if cut_percent > 0:
        milliseconds = int(len(sound) * cut_percent / 100)
        return sound[milliseconds:-milliseconds]
    return sound


def concat_sound(*sounds, cut_percent=5):
    return sum([cut_sound(sound, cut_percent) for sound in sounds])


def change_duration(sound: str | AudioSegment, duration_seconds: float = 1) -> AudioSegment:
    if type(sound) is str:
        sound = AudioSegment.from_mp3(sound)
    length_max = int(duration_seconds * 1000)
    if len(sound) >= length_max:
        return sound[:length_max]
    length: float = duration_seconds / sound.duration_seconds
    # cursor = length % 1
    # new_sound = []
    # i = 0
    # for i in range(len(sound)):
    #     segment = sound[i]
    #     while cursor >= 1:
    #         new_sound.append(segment)
    #         cursor -= 1
    #     else:
    #         cursor += length
    # while cursor >= 1:
    #     new_sound.append(sound[i])
    #     cursor -= 1
    # return sum(new_sound)
    return sound * int(length)


def speedup(sound: str | AudioSegment, speed_ratio: float = 2) -> AudioSegment:
    if type(sound) is str:
        sound = AudioSegment.from_mp3(sound)
    # noinspection PyProtectedMember
    new_sound = sound._spawn(sound.raw_data, overrides={"frame_rate": int(sound.frame_rate * speed_ratio)})
    save(new_sound, "temp.mp3")
    new_sound = read("temp.mp3")
    delete("temp.mp3")
    return new_sound


def change_volume(sound: str | AudioSegment, volume_ratio: float = 0):
    if type(sound) is str:
        sound = AudioSegment.from_mp3(sound)
    new_sound = sound + ratio_to_db(volume_ratio)
    return new_sound


def play_sound(sound: str | AudioSegment, blocking=False) -> AudioSegment:
    """ PermissionError: [Errno 13] Permission denied:
    pip install pyaudio """
    def aux():
        try:
            playback.play(sound)
        except AttributeError as e:
            # if str(e) == "'NoneType' object has no attribute 'sample_width'":
            print(traceback.format_exc() + "\n" + "file is empty", file=sys.stderr)

    try:
        if type(sound) is str:
            sound = AudioSegment.from_mp3(sound)
        if blocking:
            aux()
        else:
            Threads.run(aux)
        return sound
    except FileNotFoundError:
        print(FileNotFoundError)
        sleep(1)
        return play_sound(sound, blocking)


def save(sound: AudioSegment, dest: str):
    sound.export(dest, format="mp3")


def read(filename: str, extension="mp3"):
    import pydub
    try:
        if extension == "mp3":
            return AudioSegment.from_mp3(filename)
        elif extension == "mp4":
            return AudioSegment.from_file(filename, format="mp4")
        return AudioSegment.from_file(filename)
    except pydub.exceptions.CouldntDecodeError:
        return None


# def say(speech: str, filename=None, lang="en", speed: float = 1, blocking=False,
#         volume_ratio: float = 1, just_create_file=False, save_sound=True):
#     file_call = "python {} \"{}\" {} {} {} {} {} {} {}".format(frameinfo(1)["pathname_complete"], speech,
#                                                                filename, lang, speed,
#                                                                blocking,
#                                                                volume_ratio, just_create_file,
#                                                                save_sound)
#     # def aux():
#     run_file(file_call)
#     # Threads.run(aux)


def say(speech: str, filename=None, lang="en", speed: float = 1, blocking=False,
        volume_ratio: float = 0.5, just_create_file=False, save_sound=True, other_process=False, debug=True):
    """ TODO bug quand il y a des read input, faire la manipulation ci-dessous ou executer ce fichier en lui envoyant les arguments
    In PyCharm, if endless execution through this call, go to "Edit configuration" and mark "Emulate terminal in output console" """
    if debug:
        print("say", speech)
    if other_process:
        fi = frameinfo(1)
        # print(".", fi["pathname"] + r"alert.cmd " + " ".join(map(str, list(fi["local_args"].items())[:10])))
        Threads.run(run_file, {"file": fi["pathname"] + r"alert.cmd " + " ".join(map(str, list(fi["local_args"].values())[:10]))})
        return
    if filename is None:
        encode = blake2b(digest_size=32)
        # encode = blake2b(digest_size=4)
        encode.update(bytes(speech.encode('utf-8')))
        encode.update(bytes(lang.encode('utf-8')))
        encode.update(bytes(str(speed).encode('utf-8')))
        encode.update(bytes(str(volume_ratio).encode('utf-8')))
        filename = encode.hexdigest()
    pathname = "{}{}Sounds{}mp3{}".format(os.getcwd(), os.path.sep, os.path.sep, os.path.sep)
    if not os.path.exists(pathname):
        Path(pathname).mkdir(parents=True, exist_ok=True)
    filename = pathname + filename + ".mp3"
    if is_file_exists(filename):
        sound = read(filename, "mp3")
    else:
        tts = gTTS(text=speech, lang=lang, slow=False)
        # try:
        tts.save(filename)
        # except gtts.tts.gTTSError:
        #     print("Need an internet connection")
        #     exit(1)
        sound = read(filename)
        sound = speedup(sound, speed_ratio=speed)
        sound = change_volume(sound, volume_ratio=volume_ratio)
        if save_sound:
            save(sound, filename)
    if just_create_file:
        return sound
    return play_sound(sound, blocking)


def loop_say(msg, condition: Classes.Condition, seconds=30, blocking=True):
    def fun():
        while not condition.is_done():
            say(msg)
            sleep(seconds)
        print("loop_say end", condition)

    if blocking:
        fun()
    else:
        Threads.run(fun)


def alert(msg: str, level: int = 0, after_sleep: float = 30, debug=True):
    """ Telegram message & vocal alert
    level 0: telegram message
    level 1: telegram message & vocal alert
    level 2: loop vocal alert
    level 3: loop telegram message & vocal alert
    """
    debug_change = True
    if level == 0:
        Threads.run(lambda: Telegrams.message(msg))
    elif level == 1:
        Telegrams.message(msg)
        say(msg, debug=debug)
        sleep(after_sleep)
    elif level == 2:
        while debug_change:
            say(msg, debug=debug)
            sleep(after_sleep)
    elif level == 3:
        while debug_change:
            Telegrams.message(msg)
            say(msg, debug=debug)
            sleep(after_sleep)


def notify_win(msg):
    pass
    # toaster = ToastNotifier()
    # toaster.show_toast(msg, threaded=True)


_PINGS = {}


def ping(name=None):
    if name is None:
        name = frameinfo(2)["function_name"]
    _PINGS[name] = now()


def ping_listener():
    while True:
        ping()
        for function_name, last_ping in _PINGS.items():
            if elapsed_seconds(last_ping) > 120:
                Telegrams.message(function_name + " stopped")
                sleep(5)
        sleep(1)
        # print(_PINGS)


def ping_test():
    start = now()
    while elapsed_seconds(start) < 10:
        sleep(1)
        ping()


db_proxy = Proxy()


class AliveProcess(Model):
    name = CharField()
    last_ping = DateTimeField()

    class Meta:
        database = db_proxy
        table_function = lambda model: "alive_process"
        primary_key = CompositeKey("name")

    @staticmethod
    def init_db(db):
        db_proxy.initialize(db)
        db.create_tables([AliveProcess])


def ping_is_alive(name):
    assert db_proxy.obj is not None, "PING_IS_ALIVE DATABASE IS NOT INITIALIZED"
    AliveProcess.insert(name=name, last_ping=now()).on_conflict(
        conflict_target=[AliveProcess.name], update={AliveProcess.last_ping: now()}).execute()


if __name__ == '__main__':
    while True:
        Telegrams.message("notification")
        sleep(15)
    # if len(sys.argv) <= 1:
    #     # print("b", sys.argv)
    #     alert("speech")
    #     # say("speech")
    # run(ping_test)
    # run(ping_listener)
    # speech None en 1 False 1 False True False True
    # else:
    #     args = sys.argv[-9:]
    #     speech = " ".join(sys.argv[1:-9])
    #     # print(sys.argv, args, speech)
    #     filename = None if args[0] else args[0]
    #     lang = args[1]
    #     speed = float(args[2])
    #     blocking = False if args[3] == "False" else args[3]
    #     volume_ratio = float(args[4])
    #     just_create_file = False if args[5] == "False" else args[5]
    #     save_sound = True if args[6] == "True" else args[6]
    #     say(speech, filename, lang, speed, blocking, volume_ratio, just_create_file, save_sound, False, False)
    # _say("This is a long message !", blocking=True)
    # _say("This is a long message !", speed_ratio=1.5, blocking=True)
    # alert("telegram message", after_sleep=0)
