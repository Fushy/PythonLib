import os
import os
import sys
import traceback
from time import sleep
from typing import Callable, Optional, Iterable

from selenium import webdriver
from msedge.selenium_tools import Edge, EdgeOptions
from msedge.selenium_tools.webdriver import WebDriver
from selenium.common.exceptions import InvalidArgumentException, InvalidSessionIdException, TimeoutException, \
    WebDriverException, NoSuchWindowException, StaleElementReferenceException, NoSuchElementException, \
    MoveTargetOutOfBoundsException, ElementNotInteractableException, ElementClickInterceptedException, SessionNotCreatedException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from urllib3.exceptions import NewConnectionError, MaxRetryError
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import Alert
import Classes
from Colors import printc
from Enum import FIRST
from Files import get_first_line
from Introspection import current_lines, frameinfo
from Seleniums.Selenium import profile_name, check_find_fun, get_element_text, get_element_class
from Sys import SCREENS
from Times import now, elapsed_seconds
from Util import is_iter_but_not_str

last_browser_set = now()

class Browser:
    """ If Cloudflare protection, add the Chrome Cloudflare Helper extension
        https://chromewebstore.google.com/detail/chrome-cloudflare-helper/mlfmmcdkndpcaffjdbbjoodliplkpkmj"""
    # noinspection PyTypeChecker
    def __init__(self, point=None, profile=None, headless=False):
        self.point = point
        if point is None:
            self.point = Classes.Point(0, 0)
        self.profile: str = profile
        self.headless: bool = headless
        self.working_window_num: int = 0
        self.current_window_num: int = 0
        self.windows_url: list[str] = [""]
        self.driver: WebDriver = None
        self.name: Optional[str] = None
        self.complete_name: Optional[str] = None
        frame = frameinfo(3)
        self.project_name: str = frame["filename"] if frame else None
        self.set_browser(profile)

    def __str__(self):
        return "{} {} {} {}".format(self.name, self.windows_url, self.point, self.profile)

    def __len__(self):
        try:
            return len(self.driver.window_handles)
        except WebDriverException:
            # selenium.common.exceptions.WebDriverException: Message: chrome not reachable
            sleep(1)
            try:
                return len(self.driver.window_handles)
            except WebDriverException:
                return 0

    def print(self, texts: str | Iterable, tab=True):
        """ Prend cerrtaines ms, point eviter si on veut optimiser la vitesse"""

        def aux():
            print("{}{} {}\t\t\t{} {}".format(
                "\t" if tab else "",
                self.name,
                " ¤ ".join(map(str, texts)) if is_iter_but_not_str(texts) and type(texts) is not str else texts,
                self,
                current_lines(start_depth=4)))

        # run(aux)
        aux()

    def printc(self, texts: str | Iterable, color="green", background_color=None, attributes: Optional[list] = None,
               tab=True):
        printc("{}{} {}\t\t\t{} {}".format(
            "\t" if tab else "",
            self.name,
            " ¤ ".join(map(str, texts)) if is_iter_but_not_str(texts) and type(texts) is not str else texts,
            self,
            current_lines(start_depth=3)),
            color=color,
            background_color=background_color,
            attributes=attributes)

    def set_browser(self, profile=None):
        global last_browser_set
        # Uniquement pour Edge
        """ Download drivers
            # https://pypi.org/project/selenium/
            # https://developer.microsoft.com/fr-fr/microsoft-edge/tools/webdriver/
            # https://github.com/operasoftware/operachromiumdriver/releases
            # https://github.com/mozilla/geckodriver/releases
            # https://chromedriver.chromium.org/downloads https://googlechromelabs.github.io/chrome-for-testing/
            # edge://version/ - set a profile path location to create a new profile
        """
        # try:
        self.working_window_num = 0
        self.current_window_num = 0
        self.driver = None
        self.windows_url: list[str] = [""]
        if profile is not None:
            assert "user-user-data-dir=" in profile
            self.profile = profile
        elif profile is None and self.profile is not None:
            pass
        self.name = None if self.profile is None else profile_name(self.profile)
        self.complete_name = None if not self.name or not self.project_name else self.project_name + " " + self.name
        num = get_first_line(r"C:\Windows\addins\num")
        if num != "" and profile is not None:
            end = profile[profile.find("\\Profiles\\"):]
            self.profile = r"user-user-data-dir=C:\Users\Alexis\Documents" + end
        # options = webdriver.FirefoxOptions()
        options = webdriver.ChromeOptions()
        # options = EdgeOptions()
        if self.headless:
            options.add_argument("headless")
        if self.profile is not None:
            options.add_argument(self.profile)
        options.add_argument('--disable-blink-features=AutomationControlled')

        while elapsed_seconds(last_browser_set) < 0.1:
            sleep(0.1)
        last_browser_set = now()
        pathname = frameinfo(2)["pathname"]
        # pathname = pathname if num == "" else "C:\\Users\\Alexis\\Documents\\Profiles\\"
        # exe_path = r"{}Drivers{}chromedriver{}.exe".date_format(pathname, os.path.sep, num if num else "")
        # exe_path = r"{}Drivers{}msedgedriver.exe".format(pathname, os.path.sep)
        # exe_path = r"{}Drivers{}operadriver.exe".format(pathname, os.path.sep).replace("\\", "/")
        # exe_path = r"{}Drivers{}operadriver.exe".format(pathname, os.path.sep)
        exe_path = f"{pathname}Drivers{os.path.sep}chromedriver.exe"
        # exe_path = r"{}Drivers{}msedgedriver.exe".format(pathname, os.path.sep)
        try:
            # driver = Edge(options=options, executable_path=exe_path)
            driver = webdriver.Chrome(options=options)
            driver.set_window_position(self.point.x, self.point.y)
            driver.set_window_size(1920, 1080)
            self.driver = driver
            self.print("set_browser", False)
        # except SessionNotCreatedException:
        #     printc("SessionNotCreatedException", background_color="red")
        #     while True:
        #         Alert.say("Have to download new browser driver version")
        #         sleep(3)
        except InvalidArgumentException:
            raise InvalidSessionIdException("profile is already open")
        # except WebDriverException as err:
        #     sleep(5)
        #     self.printc("WebDriverException" + str(err), color="black", background_color="red")
        #     # return self.set_browser(profile)
        #     self.quit()
        #     return Browser(SCREENS[1], profile=self.profile)

    def update_windows_url(self) -> Optional[str]:
        try:
            url = self.driver.current_url
        except (NoSuchWindowException, MaxRetryError):
            url = ""
        if url is None or len(url) <= 1:
            self.goto_last()
            return self.update_windows_url()
        else:
            self.set_windows_url(url, self.get_current_window_num() + 1)
            return url

    def current_url(self) -> Optional[str]:
        try:
            url = self.update_windows_url()
            # print(14)
            # num = self.get_current_window_num()
        except NoSuchWindowException:
            url = ""
        # except MaxRetryError:
        #     print(142)
        #     url = ""
        #     num = 0
        # print(143)
        # self.set_windows_url(url, num + 1)
        return url

    def decr_current_window_num(self):
        if len(self.windows_url) > self.current_window_num:
            del self.windows_url[self.current_window_num]
        self.current_window_num -= 1
        self.updateinfos_current_page()

    def wait_new_created_window(self, old_count=None):
        if old_count is None:
            old_count = len(self)
        start = now()
        while len(self) <= old_count:
            sleep(0.1)
            if elapsed_seconds(start) >= 5:
                return False
        return True

    def updateinfos_current_page(self):
        try:
            self.driver.switch_to.window(self.driver.window_handles[self.get_current_window_num()])
            self.update_windows_url()
        except IndexError:
            # step by step all
            self.decr_current_window_num()

    def goto(self, window_num, update_working=True) -> bool:
        try:
            if window_num >= len(self.driver.window_handles):
                return False
            self.current_window_num = window_num
            self.driver.switch_to.window(self.driver.window_handles[window_num])
            self.update_windows_url()
        except WebDriverException:
            printc("goto WebDriverException", color="black", background_color="red")
            # selenium.common.exceptions.WebDriverException: Message: unknown error: cannot activate web view
            return False
        except IndexError:
            printc("goto IndexError", color="black", background_color="red")
            # selenium.common.exceptions.WebDriverException: Message: unknown error: cannot activate web view
            return False
        if update_working:
            self.working_window_num = window_num
        return True

    def goto_main(self):
        return self.goto(FIRST)

    def goto_last(self):
        return self.goto(len(self) - 1)

    def goto_work(self):
        """ Selon le browser """
        return self.goto(self.working_window_num)

    def goto_next(self, update_working=True):
        return self.goto((self.get_current_index_window() + 1) % len(self), update_working=update_working)

    # ne peut pas faire cette methode car après un clique qui change de page, le driver n'est pas actualisé est l'ancienne page reste celle active
    # def goto_current_active_page(self):
    def goto_current_working_page(self):
        """ Selon le driver """
        return self.goto(self.get_current_index_window())

    def get_current_active_window(self) -> str:
        return self.driver.current_window_handle

    def get_current_index_window(self) -> int:
        return self.driver.window_handles.index(self.get_current_active_window())

    def set_windows_url(self, url, window_num):
        for i in range(window_num):
            # if i >= len(self):
            #     self.new_tab()
            if i >= len(self.windows_url):
                self.windows_url.append("")
        self.windows_url[window_num - 1] = url

    def new_page(self, url, window_num=None, tries=0, debug=False):
        try:
            if tries >= 5:
                return False
            if window_num is None:
                window_num = self.get_current_window_num()
            if debug:
                self.print(("new_page", url, window_num, tries), False)
            self.goto(window_num)
            self.driver.get(url)
            if debug:
                print("\t", "loaded new_page", self)
            self.update_windows_url()
        except InvalidSessionIdException as err:
            print("\terror new_page InvalidSessionIdException", str(err))
            Alert.say("error new_page InvalidSessionIdException")
            print(traceback.format_exc(), file=sys.stderr)
            return self.new_page(url, window_num, tries + 1)
        except TimeoutException as err:
            print("\terror new_page TimeoutException", str(err))
            Alert.say("error new_page TimeoutException")
            print(traceback.format_exc(), file=sys.stderr)
            return self.new_page(url, window_num, tries + 1)
        except (WebDriverException, MaxRetryError, ConnectionRefusedError, NewConnectionError) as err:
            print(
                "\terror new_page WebDriverException MaxRetryError ConnectionRefusedError NewConnectionError",
                str(err))
            Alert.say("critical error new_page")
            print(traceback.format_exc(), file=sys.stderr)
            self.relaunch()
            return self.new_page(url, window_num, tries + 1)

    def new_tab(self):
        self.updateinfos_current_page()
        self.driver.execute_script("window.open('');")
        self.set_windows_url("", self.get_current_window_num() + 1)

    def new_tab_and_go(self):
        self.goto_last()
        self.new_tab()
        self.goto_last()

    def new_url_tab(self, url):
        self.new_tab_and_go()
        self.new_page(url)

    def close_current_and_go_main(self):
        self.windows_url[self.get_current_window_num()] = ""
        self.close()
        self.goto_main()

    def close_main(self):
        index_window = self.get_current_index_window()
        self.goto_main()
        self.close()
        self.goto(index_window)

    def refresh(self):
        try:
            self.driver.refresh()
        except NoSuchWindowException:
            "selenium.common.exceptions.NoSuchWindowException: Message: no such window: target window already closed"

    def relaunch(self):
        self.quit()
        self.printc("relaunch|" + str(self.profile) + "|", color="red")
        self.set_browser(self.profile)

    def assert_url(self, wanted_url):
        try:
            if self.current_url() == "about:blank":
                browser.close()
                return self.assert_url(wanted_url)
            if wanted_url not in self.current_url():
                sleep(1)
                self.goto_work()
                if self.current_url() == "about:blank":
                    browser.close()
                    return self.assert_url(wanted_url)
                if wanted_url not in self.current_url():
                    sleep(1)
                    self.goto_current_working_page()
                    if self.current_url() == "about:blank":
                        browser.close()
                        return self.assert_url(wanted_url)
                    if wanted_url not in self.current_url():
                        # Alert.say("url is not good")
                        self.print(("url_is_not_good", wanted_url, self.current_url()))
                        self.new_page(wanted_url, self.get_current_window_num())
                    return False
            return True
        except NoSuchWindowException:
            #     """NoSuchWindowException: Si la fenetre n'existe plus"""
            #     return None
            self.goto_work()
            return None

    def get_current_window_num(self):
        try:
            return self.driver.window_handles.index(self.driver.current_window_handle)
        except WebDriverException:
            return self.current_window_num
        except NoSuchWindowException:
            return self.current_window_num

    def get_current_url(self):
        return self.driver.current_url

    def close(self):
        # assert self.get_current_window_num() != 0
        self.decr_current_window_num()
        self.driver.close()
        self.goto(self.current_window_num)

    def quit(self):
        self.windows_url = None
        # if self.driver is not None:
        try:
            self.driver.quit()
        except AttributeError:
            pass
        self.driver = None
        sleep(5)

    def get_width(self) -> Optional[float]:
        try:
            return self.driver.get_window_size()["width"]
        except WebDriverException:
            return None

    def get_element(self,
                    selectors: str | Iterable[str],
                    find_by: str ="xpath",
                    get_one_element=True,
                    debug=False,
                    all_windows=False) \
            -> None | WebElement | list[WebElement]:
        if debug is None:
            self.print(("get_element", selectors), False)
        # if not is_elements:
        #     find_element_fun = check_find_fun(self.driver, find_element_fun_name)
        save_work_num = self.working_window_num
        for i in range(len(self)):
            if i != 0:
                self.goto_next(update_working=True)
            try:
                if type(selectors) is str:
                    selectors = [selectors]
                for selector in selectors:
                    elements: list[WebElement] = self.find_element(find_by, selector)
                    if get_one_element:
                        # if all_windows:
                        #     self.goto_work()
                        return elements
                    elif type(elements) == list and len(elements) > 0:
                        # if all_windows:
                        #     self.goto_work()
                        return elements[0]
                if all_windows:
                    continue
                return None
            except NoSuchWindowException or WebDriverException as err:
                # selenium.common.exceptions.NoSuchWindowException: Message: no such window: target window already closed
                # self.print("win dont exist")
                # sleep(1)
                if all_windows:
                    continue
                return None
        if all_windows:
            self.goto(save_work_num)
        return None

    def get_class(self, selector: str, find_by: str ="xpath", debug: bool = False) \
            -> Optional[WebElement]:
        if debug is None:
            self.print(("get_class", selector), False)
        return get_element_class(self.get_element(selector, find_by=find_by))

    def get_all_tag_that_contains(self,
                                  web_element,
                                  predicats_on_element: list[Callable] = (lambda x: True,),
                                  tag="div",
                                  doublon=False,
                                  alone=False) -> dict[str, WebElement] | None:
        print("get_all_tag_that_contains")
        if web_element is None:
            return None
        elements = self.get_element(tag, web_element.find_elements_by_tag_name)
        if elements is None:
            return None
        element_dict = {}
        for element in elements:
            element_text = get_element_text(element)
            if element_text is None:
                return None
            print("\tget_all_tag_that_contains_element_text<|" + str(element_text) + "|>")
            for predicat in predicats_on_element:
                if predicat(element):
                    if alone:
                        element_dict[element_text] = element
                        return element_dict
                    elif not doublon:
                        element_dict[element_text] = element
                    else:
                        if element_text not in element_dict:
                            element_dict[element_text] = []
                        element_dict[element_text].append(element)
        print("\t\n...\n".join(element_dict))
        print(len(element_dict), element_dict)
        return element_dict

    def wait_element(self,
                     url,
                     selectors: str | Iterable[str],
                     find_by: str ="xpath",
                     appear=True,
                     refresh: int = None,
                     leave: int = 60,
                     debug=False) -> WebElement | bool:
        """ Attend qu'un ou plusieurs element apparaissent ou disparaissent"""
        self.print(("wait_element", url, selectors, appear, refresh, leave), False)
        self.assert_url(url)
        start_refresh = now()
        start_leave = now()
        # if appear:
        #     # On attend que l'element apparaisse
        #     element = self.get_element(selector, find_element_fun)
        #     condition_satisfy = element is not None
        # else:
        #     # On attend que l'element disparaisse
        #     condition_satisfy = self.get_element(selector, find_element_fun) is None
        condition_satisfy = False
        while not condition_satisfy:
            self.assert_url(url)
            if appear:
                element = self.get_element(selectors, find_by)
                condition_satisfy = element is not None
                if condition_satisfy:
                    return element
            elif not appear:
                condition_satisfy = self.get_element(selectors, find_by) is None
                if condition_satisfy:
                    return True
            if debug:
                self.print((selectors, find_by, "url =", url))
            if refresh is not None and (now() - start_refresh).total_seconds() >= refresh:
                if url is not None and url != "":
                    self.new_page(url)
                else:
                    self.refresh()
                sleep(1)
                start_refresh = now()
            if debug:
                self.print(
                    ("r", refresh, (now() - start_refresh).total_seconds(),
                     "l", leave, (now() - start_leave).total_seconds(), "url =", url))
            if leave is not None and (now() - start_leave).total_seconds() >= leave:
                return False

    def big_wait_element(self,
                         url: str,
                         selector: str,
                         find_by: str ="xpath",
                         text: str = None,
                         class_text: str = None,
                         refresh: int = None,
                         leave: int = 60,
                         debug=False) -> WebElement | bool:
        """ Attend qu'un element apparaisse avec plusieurs critere restrictif"""
        self.print(("big_wait_element", url, selector, text, class_text, refresh, leave), False)
        self.assert_url(url)
        start_refresh = now()
        start_leave = now()
        while leave is None or elapsed_seconds(start_leave) < leave:
            if refresh is not None and elapsed_seconds(start_refresh) < refresh:
                self.refresh()
                start_refresh = now()
            element = self.get_element(selector, find_by)
            if element is not None:
                satisfy_text, satisfy_class = True, True
                if text is not None:
                    element_text = get_element_text(element, debug)
                    if element_text is None or text not in element_text:
                        satisfy_text = False
                if class_text is not None:
                    element_class = get_element_class(element, debug)
                    if element_class is None or class_text not in element_class:
                        satisfy_class = False
                if satisfy_text and satisfy_class:
                    return element
        return False

    def clicking_big_wait_element(self,
                                  url: str,
                                  selector: str,
                                  find_by: str ="xpath",
                                  text: str = None,
                                  class_text: str = None,
                                  element_to_click: WebElement = None,
                                  refresh: int = None,
                                  leave: int = 60,
                                  sleep_click: int = 1,
                                  debug=False) -> WebElement | bool:
        """ Attend qu'un element apparaisse avec plusieurs critere restrictif"""
        self.print(("clicking_big_wait_element", url, selector, text, class_text, sleep_click, refresh, leave), False)
        self.assert_url(url)
        start_refresh = now()
        start_leave = now()
        last_click = now()
        while leave is None or elapsed_seconds(start_leave) < leave:
            if refresh is not None and elapsed_seconds(start_refresh) < refresh:
                self.refresh()
                start_refresh = now()
            element = self.get_element(selector, find_by)
            if element is not None:
                if elapsed_seconds(last_click) >= sleep_click:
                    if element_to_click is None:
                        self.element_click(element)
                    else:
                        self.element_click(element_to_click)
                    last_click = now()
                satisfy_text, satisfy_class = True, True
                if text is not None:
                    element_text = get_element_text(element, debug)
                    if element_text is None or text not in element_text:
                        satisfy_text = False
                if class_text is not None:
                    element_class = get_element_class(element, debug)
                    if element_class is None or class_text not in element_class:
                        satisfy_class = False
                if satisfy_text and satisfy_class:
                    return element
        return False

    def get_text(self, url, selector: str | Iterable[str], find_by: str ="xpath", refresh=None, leave=None, debug=False) \
            -> Optional[str]:
        """ Retourne le texte d'un element """
        if debug is None:
            self.print(("get_text", selector, refresh, leave), False)
        self.assert_url(url)
        try:
            if leave is not None:
                if not self.wait_element(url, selector, find_by, leave=leave, debug=debug):
                    if debug:
                        self.print("get_text_2 None")
                    return None
            elif refresh is not None:
                self.wait_element(url, selector, find_by, refresh=refresh, debug=debug)
            element = self.get_element(selector, find_by)
            if element is None:
                return None
            return get_element_text(element, debug)
        except StaleElementReferenceException:
            return None

    def wait_text(self,
                  url: str,
                  selectors: Optional[str] | Optional[list[str]] = None,
                  leave=60,
                  refresh=22,
                  min_txt_len=1,
                  debug=True,
                  find_by: str ="xpath") -> Optional[str]:
        """ Retourne le texte d'un premier element trouvé"""
        self.print(("wait_text", leave, refresh, min_txt_len))
        self.assert_url(url)
        start, start_refresh = now(), now()
        while elapsed_seconds(start) < leave:
            if refresh is not None and elapsed_seconds(start_refresh) >= refresh:
                if url is not None:
                    self.new_page(url)
                else:
                    browser.refresh()
                start_refresh = now()
            if is_iter_but_not_str(selectors):
                for selector in selectors:
                    text = self.get_text(url, selector, leave=1, debug=debug, find_by=find_by)
                    if text is not None and len(text) >= min_txt_len:
                        return text
            else:
                text = self.get_text(url, selectors, leave=1, debug=debug, find_by=find_by)
                if text is not None and len(text) >= min_txt_len:
                    return text
        return None

    def move_to(self, element: Optional[WebElement]) -> None:
        self.print(("move_to", element, type(element)), False)
        ActionChains(self.driver).move_to_element(element).perform()

    def element_click(self, element: Optional[WebElement], actionchain=False, debug=False, leave=15) -> bool:
        self.print(("element_click", element, type(element)), False)
        assert type(element) is WebElement or element is None
        if element is None:
            if debug:
                self.print("element_click_element_is_None")
            return False
        try:
            if debug:
                self.print(("click_check_if_is_enable0", element.is_enabled()))
            start = now()
            while not element.is_enabled():
                if debug:
                    self.print(("click_check_if_is_enable1", element.is_enabled()))
                if elapsed_seconds(start) <= leave:
                    return False
            if debug:
                self.print(("clickA", element.is_enabled()))
            if actionchain:
                ActionChains(self.driver).click(element).perform()
            else:
                element.click()  # 5x plus rapide que ActionChains(self.driver).click(element).perform()
            return True
        except AttributeError:
            if debug:
                self.print("error_element_click")
                self.print(("click_check_if_is_enable2", element.is_enabled()))
            start = now()
            while not element.is_enabled():
                if debug:
                    self.print(("click_check_if_is_enable3", element.is_enabled()))
                if elapsed_seconds(start) <= leave:
                    return False
            if actionchain:
                element.click()
            else:
                ActionChains(self.driver).click(element).perform()
            if debug:
                self.print(("clickB", element.text))
            return True
        except StaleElementReferenceException or NoSuchWindowException:
            """N'existe plus"""
            return False
        except MoveTargetOutOfBoundsException:
            """N'est plus dans le champs cliquable"""
            return False
        except ElementNotInteractableException:
            """N'est plus dans le champs cliquable"""
            return False
        except ElementClickInterceptedException:
            """selenium.common.exceptions.ElementClickInterceptedException: Message: element click intercepted: 
            Element <img src="https://mypinata.cloud/ipfs/QmVy4xphMjDCYGmzQR6FhU8E6gHEaMpKbzf39wKFyqNBVV" alt="1" 
            class="carousel__img--item"> is not clickable at point (653, 377). Other element would receive the click"""
            return False

    def get_element_n_click(self, selector, find_element_fun=None) -> bool:
        element = self.get_element(selector, find_element_fun)
        return self.element_click(element)

    def wait_element_n_click(self, url, selector, find_element_fun=None, refresh=None, leave=None,
                             sleep_after_find=0) -> bool:
        element = self.wait_element(url, selector, find_element_fun, refresh=refresh, leave=leave)
        if type(element) is bool:
            return False
        sleep(sleep_after_find)
        return self.element_click(element)

    def click_n_wait_new_created_window(self, element: WebElement) -> bool:
        old_count_window = len(self)
        self.element_click(element)
        return self.wait_new_created_window(old_count_window)

    def click_recaptcha(self):
        try:
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame(self.driver.find_element(By.XPATH, ".//iframe[@title='reCAPTCHA']"))
            self.driver.find_element(By.ID, "recaptcha-anchor-label").click()
            self.driver.switch_to.default_content()
            sleep(1.5)
            "/html/body/div"
        except (NoSuchElementException, ElementClickInterceptedException):
            pass

    def element_send(self, element: WebElement, *keys, debug=True):
        if debug:
            self.print(("element_send", keys), False)
        if element is None:
            if debug:
                self.print("element_send_is_None")
            return
        try:
            keys = list(map(str, keys))
            actions = ActionChains(element)
            for key in keys:
                actions.send_keys(key)
            actions.perform()
        except AttributeError:
            try:
                ActionChains(element).send_keys_to_element(keys)
            except AttributeError:
                try:
                    # sleep(0.1)
                    for key in keys:
                        element.send_keys(key)
                    # element.send_keys(keys)
                except AttributeError as err:
                    if debug:
                        print("\terror element_send", err)
                    # sleep(0.5)
                    self.element_send(element, keys)
            except StaleElementReferenceException:
                """N'existe plus"""

    def clear_send(self, element):
        for _ in range(10):
            self.element_send(element, Keys.BACK_SPACE)

    def wait_url(self, url, leave=5, strict=False):
        start = now()
        while not ((strict and url == self.current_url()) or (not strict and url in self.current_url())):
            sleep(0.01)
            if elapsed_seconds(start) >= leave:
                return False
        return True

    def accept_popup(self):
        confirmation_popup = WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        confirmation_popup.accept()

    def find_element(self, find_by, selector):
        try:
            return self.driver.find_element(find_by, selector)
        except NoSuchElementException:
            pass

def get_all_attributes(driver: WebDriver, element: WebElement) -> dict[str, str]:
    """ If None, try to get a child """
    return driver.execute_script("""
        let attributes = {};
        let element = arguments[0];
        let attrs = element.attributes;
        for(let i = 0; i < attrs.length; i++) {
            attributes[attrs[i].name] = attrs[i].value;
        }
        return attributes;
    """, element)

# def scrap_google_search():
#     countries = [(country.name.split(",")[0] if "," in country.name else country.name) for country in
#                  pycountry.countries]
#     # countries = ["Liberia"]
#     shuffle(countries)
#     wanted_values = ["capital", "population", "area", "timezones"]
#     for country in countries:
#         for values in wanted_values:
#             url = "https://www.google.com/search?q=" + values + " of " + country
#             browser.new_page(url, debug=False)
#             a = browser.get_element("/html/body/div[3]/div[3]/span/div/div/div/div[3]/div[1]/button[2]/div",
#                                     debug=False)
#             if a is not None:
#                 a.click()
#             result = browser.get_text("", "HwtpBd", browser.driver.find_element_by_class_name, debug=False)
#             if result is None or len(result) <= 3:
#                 result = browser.get_text("", "ayqGOc", browser.driver.find_element_by_class_name, debug=False)
#             if result is None or len(result) <= 3:
#                 result = browser.get_element("vk_gy", browser.driver.find_element_by_class_name, debug=False)
#                 if result is not None:
#                     result = result.find_elements_by_tag_name("div")[1].text
#                     result = result[result.find("\""):].replace("\"", "")
#             if result is not None:
#                 is_date_present = re.compile(r"[(][0-9]{4}[)]").search(result)
#                 if is_date_present:
#                     result = result.replace(is_date_present.group(), "")
#                 result = result.replace(" ", "").replace(" ", "")
#                 is_float_present = re_float.search(result)
#                 if is_float_present:
#                     is_float_present = is_float_present.group().replace(",", ".")
#                     result = float(is_float_present) * (1000000 if "million" in result else 1)
#                 countries_dict[country][values] = result
#             print(country, "-", result)
#     input("end")

if __name__ == '__main__':
    ## s = screen_rect(1000)
    # browser = Browser(profile=r"user-user-data-dir=B:\_Documents\Ragnarok_uaro")
    browser = Browser()
    # # r"user-user-data-dir=C:\Users\alexi_mcstqby\Documents\Bots\AlienWorlds\Profiles\progk")
    # browser.new_page('https://www.expressvpn.com/what-is-my-ip')
    # browser.new_page('https://fr.tradingview.com/chart/dOWkigGU/?symbol=BINANCE%3ABTCBUSD')
    browser.new_page('https://uaro.net/')
    # browser.new_page('https://google.com')

    # from selenium.webdriver.chrome.service import Service
    # from selenium.webdriver.common.by import By
    # from selenium.webdriver.support.ui import WebDriverWait
    # from selenium.webdriver.support import expected_conditions as EC
    # from webdriver_manager.chrome import ChromeDriverManager
    # options = webdriver.ChromeOptions()
    # options.add_argument('--disable-blink-features=AutomationControlled')
    # driver = webdriver.Chrome(options=options)
    # driver.get('https://uaro.net/')
    # input()
