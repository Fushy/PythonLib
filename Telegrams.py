import asyncio
import os
import threading
import time

from dotenv import load_dotenv
from telegram import Bot

from Threads import run
from Times import now

USER_IDS = {"ale": 1522961892}
load_dotenv()


async def send_telegram_message(api_key, chat_id, text):
    bot = Bot(token=api_key)
    print(now(), "telegram send", f"|{text[:1000]}|")
    await bot.send_message(chat_id=chat_id, text=text[:1000])
    return True


async def message_async(msg: str, to: str = None):
    if to is None:
        id_to = USER_IDS["ale"]
    else:
        id_to = USER_IDS[to]

    api_key = os.getenv("TELEGRAM_API_KEY")
    if not api_key:
        print("Error: TELEGRAM_API_KEY not found in .env file")
        return
    await send_telegram_message(api_key, id_to, msg)


telegram_global_loop = None
telegram_loop_thread = None
telegram_loop_ready = threading.Event()


def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def get_event_loop():
    global telegram_global_loop, telegram_loop_thread
    if telegram_global_loop is None:
        with threading.Lock():
            if telegram_global_loop is None:
                telegram_global_loop = asyncio.new_event_loop()

                telegram_loop_thread = threading.Thread(
                    target=start_background_loop,
                    args=(telegram_global_loop,),
                    daemon=True
                )
                telegram_loop_thread.start()
                time.sleep(0.5)

    return telegram_global_loop


def message(msg: str, to: str = None):
    """Send a Telegram message asynchronously using a background event loop.
    This function schedules the message send but does not wait for completion. If you need to ensure all messages are sent before proceeding or exiting the
    program, you must explicitly wait (e.g., using `threading.Event().wait()` in the main thread) or modify this function to block until the send is complete.
    Without a wait mechanism, the program may exit before messages are fully sent, especially in short-lived scripts."""
    loop = get_event_loop()

    # Add a safety check to ensure loop is not None
    if loop is None:
        raise RuntimeError("Failed to create event loop")

    asyncio.run_coroutine_threadsafe(message_async(msg, to), loop)


def aux():
    message("message aaa")


if __name__ == "__main__":
    profiles_dir = os.getenv("BROWSER_PROFILES")
    aux()
    aux()
    run(aux)
    run(aux)
    # threading.Event().wait()