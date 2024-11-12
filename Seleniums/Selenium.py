import os
from time import sleep
from typing import Callable, Optional

from msedge.selenium_tools.webdriver import WebDriver
from selenium.common.exceptions import NoAlertPresentException, \
    StaleElementReferenceException
from selenium.webdriver import Chrome, ChromeOptions
# from selenium.webdriver.opera.webdriver import OperaDriver
from selenium.webdriver.remote.webelement import WebElement

from Alert import notify_win
from Classes import Point
from Introspection import frameinfo
from Times import now, elapsed_seconds


def create_opera_browser(x, y=None, profile=None, headless=False):
    if type(x) is Point:
        y = x.y
        x = x.x
    options = ChromeOptions()
    # options = Options()
    options.binary_location = "A:\Opera\launcher.exe"
    # if headless:
    #     # options.headless = True
    #     options.add_argument("headless")
    # if profile is not None:
    #     options.add_argument(profile)
    # print(r"{}{}Selenium{}Drivers{}operadriver.exe"
    #                       .date_format(os.getcwd(), os.path.sep, os.path.sep, os.path.sep))
    browser = OperaDriver(
        options=options, executable_path=r"{}{}Selenium{}Drivers{}operadriver.exe"
            .format(os.getcwd(), os.path.sep, os.path.sep, os.path.sep))
    browser.set_window_size(1920, 1080)
    browser.set_window_position(x, y)
    return browser


def create_chrome_browser(x, y=None, profile=None, headless=False):
    if type(x) is Point:
        y = x.y
        x = x.x
    options = ChromeOptions()
    if headless:
        # options.headless = True
        options.add_argument("headless")
    if profile is not None:
        options.add_argument(profile)
    browser = Chrome(
        options=options, executable_path=r"{}{}Selenium{}Drivers{}chromedriver.exe"
            .format(os.getcwd(), os.path.sep, os.path.sep, os.path.sep))
    browser.set_window_size(1920, 1080)
    browser.set_window_position(x, y)
    return browser


def profile_name(profile: str):
    start = profile.rindex(os.path.sep)
    name = profile[start + len(os.path.sep):]
    return name


def new_active_tab(browser: WebDriver):
    new_tab(browser)
    browser.switch_to.window(browser.window_handles[-1])


def new_url_tab(browser: WebDriver, url: str, profile=None):
    new_active_tab(browser)
    new_page(browser, url, profile, onglet_num=-1)
    browser.switch_to.window(browser.window_handles[-1])


def new_url_tab_off(browser: WebDriver, url: str, profile):
    save = browser.current_window_handle
    new_active_tab(browser)
    new_page(browser, url, profile, onglet_num=-1)
    new = browser.current_window_handle
    browser.switch_to.window(save)
    return new


def close_current_and_create_new(browser: WebDriver, url: str, profile):
    new_tab(browser)
    close_current_and_go_home(browser)
    new_page(browser, url, profile)


def metamask_accept(browser):
    print("metamask_accept")
    pop_up_exist = wait_popup(browser)
    if pop_up_exist is not True:
        return False
    browser.switch_to.window(browser.window_handles[-1])
    fee = metamask_get_fee_gas(browser)
    if float(fee) >= 0.01:
        print("\tfee is too high", fee)
        return
    metamask_confirm(browser)
    browser.switch_to.window(browser.window_handles[0])
    return fee


def metamask_wait_connect(browser, msg="", wait_sec=0.5):
    print("metamask_wait_connect")
    start = now()
    while len(browser.window_handles) < 2:
        print("\twindows", len(browser.window_handles), elapsed_seconds(start))
        sleep(0.5)
        if elapsed_seconds(start) % wait_sec == 0:
            start = now()
            browser.refresh()
        if elapsed_seconds(start) >= 5:
            break
    notify_win("start metamask " + msg)
    while len(browser.window_handles) >= 2:
        metamask_rejeter_xpath = "/html/body/div[1]/div/div[3]/div/div[3]/div[3]/footer/button[1]"
        metamask_rejeter = get_element_check_all_windows(browser, metamask_rejeter_xpath)
        print("\twindows", len(browser.window_handles), "\tmetamask_rejeter", metamask_rejeter)
        sleep(2)
        while metamask_rejeter is not None:
            element_click(browser, metamask_rejeter)
            sleep(2)
            metamask_rejeter = None
    browser.switch_to.window(browser.window_handles[0])
    return True


def metamask_confirm(browser):
    print("metamask_confirm")
    confirm_button_xpath = "/html/body/div[1]/div/div[3]/div/div[3]/div[3]/footer/button[2]"
    confirm_button = get_element(browser, confirm_button_xpath)
    element_click(browser, confirm_button)


def metamask_get_fee_gas(browser):
    print("metamask_get_fee_gas")
    gas_fee_bnb_xpath1 = "/html/body/div[2]/div/div/section/div/div/div[2]/div[2]/div[1]/div[6]/div[2]/div/span[1]"
    gas_fee_bnb_xpath2 = "/html/body/div[1]/div/div[3]/div/div[3]/div[2]/div/div/div/div[2]/div[2]/div[1]/h6[" \
                         "3]/div/span[1]"
    gas_fee_bnb = None
    while gas_fee_bnb is None:
        gas_fee_bnb = get_element(browser, gas_fee_bnb_xpath1)
        if gas_fee_bnb is None:
            gas_fee_bnb = get_element(browser, gas_fee_bnb_xpath2)
    gas_fee_bnb_txt = get_text(gas_fee_bnb)
    print("\t", "fee", gas_fee_bnb_txt)
    return gas_fee_bnb_txt


def wait_popup(browser, sec_max=15):
    print("wait_popup")
    start = now()
    while len(browser.window_handles) < 2:
        print(len(browser.window_handles))
        sleep(0.5)
        if sec_max is not None and elapsed_seconds(start) >= sec_max:
            return elapsed_seconds(start)
    return True


def wait_popup_off(browser, sec_max=15):
    print("wait_popup_off")
    start = now()
    while len(browser.window_handles) >= 2:
        print(len(browser.window_handles))
        sleep(0.5)
        if sec_max is not None and elapsed_seconds(start) >= sec_max:
            return elapsed_seconds(start)
    return True


def metamask_get_last_fee(browser, url, profile):
    new_active_tab(browser)
    new_page(browser, url, profile, onglet_num=1)
    main_asset_xpath = "/html/body/div[1]/div/div[4]/div/div/div/div[2]/div/div[1]/div/div/div/div/div"
    if not wait_element(browser, main_asset_xpath, leave=60):
        browser.refresh()
        return metamask_get_last_fee(browser, url, profile)
    last_transaction_xpath = "/html/body/div[1]/div/div[4]/div/div/div/div[3]/div/div/div/div/div[1]"
    if not wait_element(browser, last_transaction_xpath, leave=60):
        browser.refresh()
        return metamask_get_last_fee(browser, url, profile)
    last_transaction = get_element(browser, last_transaction_xpath)
    sleep(0.5)
    element_click(browser, last_transaction)
    sleep(0.5)
    total_fee_xpath = "/html/body/div[2]/div/div/section/div/div/div[2]/div[2]/div[1]/div[7]"
    if not wait_element(browser, total_fee_xpath, leave=60):
        browser.refresh()
        return metamask_get_last_fee(browser, url, profile)
    fee_devise = get_text(browser, total_fee_xpath)
    print("\tsplit_text", fee_devise.split("\n"))
    _, fee, devise = fee_devise.split("\n")
    print("\t", fee, devise)
    close_current_and_go_home(browser)
    return fee, devise


def wait_n_click(browser, selector, find_element_fun=None, timeout=60, sleep_befor=0):
    if find_element_fun is None:
        find_element_fun = browser.find_element_by_xpath
    if not wait_element(browser, selector, leave=timeout):
        print("\t", "click element not found")
        return False
    exchange_button = find_element_fun(selector)
    sleep(sleep_befor)
    element_click(browser, exchange_button)
    return True


def is_alert_present(browser):
    try:
        browser.switch_to.window(browser.switch_to.a)
        return True
    except NoAlertPresentException:
        return False


def wait_alerte_and_close_it(browser, leave=60):
    print("wait_alerte_and_close_it")
    alert = None
    start = now()
    while alert is None:
        try:
            alert = browser.switch_to_alert()
        except NoAlertPresentException:
            alert = None
        sleep(0.5)
        if elapsed_seconds(start) >= leave:
            return None
    alert_text = alert.text
    browser.print(("alert text", alert_text))
    alert.accept()
    browser.switch_to.window(browser.window_handles[0])
    return alert_text


def get_element_text(element: Optional[WebElement], debug=False) -> Optional[str]:
    if element is None:
        return None
    try:
        element_text = element.text
    except StaleElementReferenceException:
        # selenium.common.exceptions.StaleElementReferenceException: Message: stale element reference: element is not
        # attached to the page document
        return None
    if debug:
        print("\tget_element_text <|" + element_text[:30] + "|>")
    return element_text


def get_element_class(element: WebElement, debug=False):
    if element is None:
        return None
    try:
        element_class = element.get_attribute("class")
    except StaleElementReferenceException:
        element_class = None
    if debug:
        print("\tget_element_class <|" + element_class[:30] + "|>")
    return element_class


def get_element_href(element: WebElement):
    try:
        data = element.get_attribute("href")
    except StaleElementReferenceException:
        data = None
    return data

def get_element_innerHTML(element: WebElement):
    try:
        data = element.get_attribute("innerHTML")
    except StaleElementReferenceException:
        data = None
    return data

def get_element_attribute(element: WebElement, attribute: str):
    try:
        data = element.get_attribute(attribute)
    except StaleElementReferenceException:
        data = None
    return data


def get_element_src(element: WebElement):
    try:
        data = element.get_attribute("src")
    except StaleElementReferenceException:
        data = None
    return data


def get_element_xpath(element: WebElement):
    """
    private String generateXPATH(WebElement childElement, String current) {
        String childTag = childElement.getTagName();
        if(childTag.equals("html")) {
            return "/html[1]"+current;
        }
        WebElement parentElement = childElement.findElement(By.xpath(".."));
        List<WebElement> childrenElements = parentElement.findElements(By.xpath("*"));
        int count = 0;
        for(int i=0;i<childrenElements.size(); i++) {
            WebElement childrenElement = childrenElements.get(i);
            String childrenElementTag = childrenElement.getTagName();
            if(childTag.equals(childrenElementTag)) {
                count++;
            }
            if(childElement.equals(childrenElement)) {
                return generateXPATH(parentElement, "/" + childTag + "[" + count + "]"+current);
            }
        }
        return null;
    }
    """
    return element.get_attribute("xpath")


def check_find_fun(driver: WebDriver, find_element_fun_name: str) -> Callable[[WebDriver], str]:
    find_element_fun = None
    if find_element_fun_name == "find_element_by_class_name":
        find_element_fun = lambda x: driver.find_element(value=x, by="class name")
    elif find_element_fun_name == "find_element_by_css_selector":
        find_element_fun = lambda x: driver.find_element(value=x, by="css selector")
    elif find_element_fun_name == "find_element_by_xpath":
        find_element_fun = lambda x: driver.find_element(value=x, by="xpath")
    elif find_element_fun_name == "find_element_by_tag_name":
        find_element_fun = lambda x: driver.find_element(value=x, by="tag name")
    return find_element_fun


def get_element_check_all_windows(browser, selector, find_element_fun=None):
    print("get_element_check_all_windows", selector)
    element = None
    for i in range(len(browser.window_handles)):
        element = get_element(browser, selector, find_element_fun)
        if element is not None:
            break
        try:
            browser.switch_to.window(browser.window_handles[i])
        except IndexError:
            pass
    return element


def get_profile_path(name: str):
    filename = frameinfo(2)["filename"]
    return "user-data-dir={}Profiles{}{}{}{}".format(os.getcwd()[:-len(filename)], os.path.sep, filename, os.path.sep, name)
