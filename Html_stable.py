import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession

AGENT = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}


def get_html_bs4(url):
    response = requests.get(url, headers=AGENT)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def get_html_dynamic_bs4(url):
    r""" https://chromium.woolyss.com/ C:\Users\alexi\AppData\Local\pyppeteer\pyppeteer\local-chromium\1181205\chrome-win"""
    session = HTMLSession()
    session = session.get(url, headers=AGENT)
    session.html.render()
    content = session.html.html
    return BeautifulSoup(content, 'html.parser')


if __name__ == '__main__':
    # bs4 = get_html_dynamic_bs4(f"https://brute.eternaltwin.org/Fushy/cell")
    # print(bs4.text)
    from loguru import logger
    logger.debug("That's it, beautiful and simple logging!")
