import re
from functools import wraps
from sys import stderr
from time import sleep
from typing import Callable, Dict, List, Optional

import undetected_chromedriver as uc
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException, MoveTargetOutOfBoundsException, NoSuchElementException, NoSuchWindowException, SessionNotCreatedException, StaleElementReferenceException, TimeoutException, WebDriverException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from Classes import Point
from Paths import SEP
from Threads import run
from Times import elapsed_seconds, now
from Util import getenv


def get_all_attributes(element):
    driver = element._parent
    attributes = driver.execute_script(
        """
        var items = {};
        for (index = 0; index < arguments[0].attributes.length; ++index) {
            items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value;
        }
        return items;
        """,
        element
    )
    return attributes

def wait_for_element(timeout=5):
    """Decorator to wait for an element to be present."""

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Extraire le timeout des kwargs si présent, sinon utiliser la valeur par défaut
            wait_timeout = kwargs.pop('timeout', timeout)
            try:
                return WebDriverWait(self.get_working_page(), wait_timeout).until(
                    lambda driver: func(self, *args, **kwargs)
                )
            except TimeoutException:
                self.print(f"Timeout waiting {wait_timeout}s for element in {func.__name__}")
                return None

        return wrapper

    return decorator


def get_element_text(element: Optional[WebElement], debug=False) -> Optional[str]:
    if element is None:
        return None
    try:
        element_text = element.text
    except (StaleElementReferenceException, WebDriverException):
        # selenium.common.exceptions.StaleElementReferenceException: Message: stale element reference: element is not attached to the page document
        return None
    if debug:
        print("\tget_element_text <|" + element_text[:30] + "|>")
    return element_text


class SeleniumBrowser:
    def __init__(self, point: Point, headless: bool = True, debug: bool = False, profile: Optional[str] = None):
        """Initialize the Selenium WebDriver with optional debug and profile settings."""
        from selenium.webdriver.chrome.service import Service
        if profile:
            profile_dir = getenv("USER_DATA_DIR")
            profile = f"{profile_dir}{SEP}Selenium{SEP}{profile}"
        service = Service(r"A:\Pycharm\Util\Seleniums\Drivers\chromedriver.exe")
        service = Service(r"A:\Pycharm\Scraping\user-data-dir\Selenium\chromedriver.exe")
        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36")
        # options.add_argument("start-maximized")
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # options.add_experimental_option("useAutomationExtension", False)

        # Handle headless mode
        if headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")  # Often required for headless

        if profile:
            options.add_argument(f"--user-data-dir={profile}")
        options.add_argument(f"--window-position={point.x},{point.y}")
        try:
            self.driver = uc.Chrome(options=options, service=service)
        except SessionNotCreatedException as e:
            if "session not created: cannot connect to chrome" in e.msg:
                # https://chromedriver.chromium.org/downloads "
                print(e, r"SessionNotCreatedException\nDownload chromedriver & update main driver\n"
                         r"https://googlechromelabs.github.io/chrome-for-testing/ & chrome://settings/help & A:\Documents\Dev\Python\Util\Seleniums\Drivers",
                      file=stderr)
            exit()

        # stealth(self.driver,
        #         languages=["en-US", "en"],
        #         vendor="Google Inc.",
        #         platform="Win32",
        #         webgl_vendor="Intel Inc.",
        #         renderer="Intel Iris OpenGL Engine",
        #         fix_hairline=True)

        self.driver.set_window_size(1920, 1080)
        self.debug = debug
        self.print(f"SeleniumBrowser initialized at {point.x},{point.y}, headless={headless}, profile={profile}")

    def __enter__(self):
        """Enter the context, returning the browser instance."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the context, automatically closing the browser."""
        try:
            run(lambda: self.close())
            self.driver.quit()
        except Exception:
            pass

    def __del__(self):
        """Cleanup method to close the browser when the object is destroyed."""
        try:
            if self.driver:
                run(lambda: self.driver.quit())
        except Exception:
            pass

    def load(self, url: str):
        """Load a URL in the browser."""
        self.driver.get(url)
        self.print(f"Loaded URL: {url}")

    def new_page(self, url: Optional[str] = None, new_tab=True):
        """Open a new tab and optionally load a URL."""
        current_page = len(self.driver.window_handles)
        while new_tab and current_page == len(self.driver.window_handles):
            self.driver.switch_to.new_window('tab')
            sleep(0.1)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        if url:
            self.load(url)
        self.print(f"New page opened, total tabs: {len(self.driver.window_handles)}")

    def goto(self, window_num) -> bool:
        if window_num >= len(self.driver.window_handles):
            return False
        self.driver.switch_to.window(self.driver.window_handles[window_num])
        return True

    def close_page(self):
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.print(f"Page closed, total tabs: {len(self.driver.window_handles)}")

    def get_pages_amount(self):
        """Get the number of pages."""
        return len(self.driver.window_handles)

    def get_working_page(self):
        """Get the current WebDriver instance."""
        return self.driver

    def get_current_url(self) -> str:
        """Return the URL of the current working page."""
        return self.driver.current_url

    def get_working_url(self) -> str:
        """Return the URL of the current working page."""
        return self.get_working_page().current_url

    def print(self, *messages):
        if self.debug:
            print(now(), *messages)
            # print(now(), end=" ")
            # print(*messages)

    def get_all_attributes(self, element: WebElement) -> Dict[str, str]:
        """Get all attributes of a WebElement."""
        if element:
            return self.driver.execute_script(
                "var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) "
                "{ items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;",
                element
            )

    def wait_element(self, fun: Callable, appear=True, refresh: int = None, leave: int = 60):
        """ Attend qu'une condition soit satisfaite (apparition ou disparition d'éléments) """
        self.print("wait_element", fun, appear, refresh, leave)
        start_refresh, start_leave = now(), now()
        condition_satisfy = False
        while not condition_satisfy:
            result = fun()
            condition_satisfy = result is not None
            if appear and condition_satisfy:
                return result
            elif not appear and condition_satisfy:
                return True
            self.print(fun.__name__ if hasattr(fun, "__name__") else "function", "appear =", appear)
            if refresh is not None and (now() - start_refresh).total_seconds() >= refresh:
                if hasattr(self, "refresh"):
                    self.refresh()
                    sleep(1)
                    start_refresh = now()
            self.print("r", refresh, (now() - start_refresh).total_seconds(), "l", leave, (now() - start_leave).total_seconds())
            if leave is not None and (now() - start_leave).total_seconds() >= leave:
                return False
        return None

    @wait_for_element(timeout=0.1)
    def get_element(self, selector: str, element=None) -> WebElement:
        """Get the first element matching a CSS selector."""
        base = element if element else self.get_working_page()
        return base.find_element(By.CSS_SELECTOR, selector)

    def get_element_id(self, id_: str, element=None) -> WebElement:
        """Get the first element by ID."""
        selector = f"#{id_}"
        self.print(f"Searching for element by ID: {selector}")
        return self.get_element(selector, element)

    def get_element_class(self, class_name: str, element=None, timeout: float = 0.1) -> WebElement:
        """Get the first element by class name (supports multiple classes)."""

        self.driver.switch_to.window(self.driver.window_handles[-1])
        selector = "".join(f".{cls}" for cls in class_name.split())
        self.print(f"Searching for element by class: {selector}")
        return self.get_element(selector, element, timeout=timeout)

    def get_element_test_id(self, test_id: str, element=None) -> WebElement:
        """Get the first element by data-testid."""
        selector = f"[data-testid='{test_id}']"
        self.print(f"Searching for element by test ID: {selector}")
        return self.get_element(selector, element)

    def get_element_aria_label(self, aria_label: str, tag_name: Optional[str] = None, element=None) -> WebElement:
        """Get the first element by aria-label."""
        selector = f"{tag_name or '*'}[aria-label='{aria_label}']"
        self.print(f"Searching for element by aria-label: {selector}")
        return self.get_element(selector, element)

    def get_element_input_type(self, input_type: str, element=None) -> WebElement:
        """Get the first input element by type."""
        selector = f"input[type='{input_type}']"
        self.print(f"Searching for input by type: {selector}")
        return self.get_element(selector, element)

    @wait_for_element(timeout=1)
    def get_element_tag(self, tag_name: str, element=None) -> WebElement:
        """Get the first element by tag name."""
        self.print(f"Searching for element by tag: {tag_name}")
        base = element if element else self.get_working_page()
        return base.find_element(By.TAG_NAME, tag_name)

    @wait_for_element(timeout=1)
    def get_element_xpath(self, xpath: str, element=None) -> WebElement:
        """Get the first element by XPath."""
        self.print(f"Searching for element by XPath: {xpath}")
        base = element if element else self.get_working_page()
        return base.find_element(By.XPATH, xpath)

    def get_element_attributes(self, tag: str, attributes: str, exists: list = None, element=None) -> WebElement:
        """Get the first element matching the tag name and attributes from a string.
        attributes = 'disabled="" type="button" aria-label="Envoyer le message"'
        exists = optional list of attributes that must exist on the element (e.g. ["aria-label"])
        """
        attr_pattern = r'(\w+(?:-\w+)*)\s*=\s*"(.*?)"'
        attributes_dict = dict(re.findall(attr_pattern, attributes.strip()))
        if not attributes_dict:
            raise ValueError("No valid attributes found in the string. Expected: 'attr=\"value\" ...'")

        selector = tag
        for attr, value in attributes_dict.items():
            if attr == "class":
                selector += "".join(f".{cls}" for cls in value.split())
            else:
                selector += f"[{attr}='{value}']"

        # Add existence checks for required attributes
        if exists:
            for attr in exists:
                if attr not in attributes_dict:
                    # Add attribute existence check without specifying a value
                    selector += f"[{attr}]"

        self.print(f"Searching for selector: {selector}")
        try:
            return self.get_element(selector, element)
        except TimeoutException:
            self.print(f"Element with selector '{selector}' not found after 1 second")
            raise

    def get_direct_children(self, element) -> list:
        return self.driver.execute_script("return arguments[0].children;", element)

    def get_elements(self, element: Optional[WebElement] = None, tag_name: Optional[str] = None,
                     id_: Optional[str] = None, text: Optional[str] = None, xpath: Optional[str] = None,
                     role: Optional[str] = None, label: Optional[str] = None, placeholder: Optional[str] = None,
                     alt_text: Optional[str] = None, title: Optional[str] = None, test_id: Optional[str] = None,
                     class_name: Optional[str] = None, style: Optional[str] = None, exact: bool = False,
                     wait_results: bool = False, wait_text: int = 0, timeout: int = 30, **role_attributes) -> List[WebElement]:
        """Get all elements matching ALL provided criteria (AND condition).

        Args:
            element: Optional WebElement to search within (default: entire page).
            tag_name: HTML tag name (e.g., 'article').
            id_: CSS ID (e.g., 'main').
            text: Visible text (e.g., 'Click me').
            xpath: XPath expression (overrides other criteria if provided).
            role: ARIA role (e.g., 'button').
            label: Associated label text.
            placeholder: Placeholder text.
            alt_text: Alt text.
            title: Title attribute.
            test_id: Data-testid attribute.
            class_name: CSS class (supports multiple, e.g., 'flex item').
            style: Style attribute.
            exact: If True, text matches are exact.
            wait_results: If True, wait for elements.
            timeout: Wait timeout in seconds.
            **role_attributes: Additional role attributes (e.g., name='submit').

        Returns:
            List[WebElement]: Elements matching all criteria.
        """
        criteria = {
            "tag_name": tag_name, "id": id_, "text": text, "xpath": xpath, "role": role, "label": label,
            "placeholder": placeholder, "alt_text": alt_text, "title": title, "test_id": test_id,
            "class_name": class_name, "style": style
        }
        if not any(criteria.values()):
            raise ValueError("At least one criterion must be provided")

        base = element if element is not None else self.get_working_page()

        # If xpath is provided, use it exclusively
        if xpath:
            by, selector = By.XPATH, xpath
        else:
            # Build a CSS selector with AND conditions
            selector = tag_name or '*'
            if id_:
                selector += f"#{id_}"
            if test_id:
                selector += f"[data-testid='{test_id}']"
            if class_name:
                selector += "".join(f".{cls}" for cls in class_name.split())
            if role:
                selector += f"[role='{role}']" + "".join(f"[{k}='{v}']" for k, v in role_attributes.items())
            if placeholder:
                selector += f"[placeholder='{placeholder}']"
            if alt_text:
                selector += f"[alt='{alt_text}']"
            if title:
                selector += f"[title='{title}']"
            if style:
                selector += f"[style='{style}']"
            by = By.CSS_SELECTOR

        # Fetch elements
        elements = []
        if wait_results or wait_text:
            if wait_results:
                try:
                    elements = WebDriverWait(base, timeout).until(
                        EC.presence_of_all_elements_located((by, selector))
                    )
                except TimeoutException:
                    if self.debug:
                        self.print(f"Timeout waiting {timeout}s for {by}: {selector}")
            if wait_text:
                try:
                    def check_text_in_elements(driver):
                        found_elements = base.find_elements(by, selector)
                        for element in found_elements:
                            if len(element.text) >= wait_text:
                                # print(element.text)
                                return found_elements
                        return False

                    elements = WebDriverWait(base, timeout).until(check_text_in_elements)
                except TimeoutException:
                    if self.debug:
                        self.print(f"Timeout waiting {timeout}s for at least {wait_text} elements with {by}: {selector}")
        else:
            try:
                elements = base.find_elements(by, selector)
            except NoSuchElementException:
                if self.debug:
                    self.print(f"No elements found with {by}: {selector}")

        # Apply filters for criteria not in CSS
        if text:
            elements = [e for e in elements if (text == e.text if exact else text in (e.text or ""))]
        if label:
            elements = [e for e in elements if any(
                label == lbl.text if exact else label in (lbl.text or "")
                for lbl in base.find_elements(By.XPATH, ".//label")
                if e in lbl.find_elements(By.XPATH, ".//*")
            )]

        if self.debug:
            self.print(f"Found {len(elements)} elements with {by}: {selector}")
        return elements

    def element_click(self, element: Optional[WebElement], actionchain=False, debug=False, leave=15) -> bool:
        self.print("element_click", element, type(element))
        assert "WebElement" in str(type(element)) or element is None
        if element is None:
            if debug:
                self.print("element_click_element_is_None")
            return False
        try:
            if debug:
                self.print("click_check_if_is_enable0", element.is_enabled())
            start = now()
            while not element.is_enabled():
                if debug:
                    self.print("click_check_if_is_enable1", element.is_enabled())
                if elapsed_seconds(start) <= leave:
                    return False
            if debug:
                self.print("clickA", element.is_enabled())
            if actionchain:
                ActionChains(self.driver).click(element).perform()
            else:
                element.click()  # 5x plus rapide que ActionChains(self.driver).click(element).perform()
            return True
        except AttributeError:
            if debug:
                self.print("error_element_click")
                self.print("click_check_if_is_enable2", element.is_enabled())
            start = now()
            while not element.is_enabled():
                if debug:
                    self.print("click_check_if_is_enable3", element.is_enabled())
                if elapsed_seconds(start) <= leave:
                    return False
            if actionchain:
                element.click()
            else:
                ActionChains(self.driver).click(element).perform()
            if debug:
                self.print("clickB", element.text)
            return True
        except (StaleElementReferenceException, NoSuchWindowException):
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

    def element_send(self, *keys, element: WebElement = None, debug=True):
        if self.debug:
            self.print("element_send", *keys)
        try:
            keys_str = ''.join(map(str, keys))
            if element is None:
                ActionChains(self.driver).send_keys(keys_str).perform()
            else:
                element.clear()
                element.send_keys(keys_str)
        except AttributeError as e:
            if debug:
                print("\terror element_send", e)
            try:
                # Same correction here
                ActionChains(self.driver).send_keys_to_element(element, *keys).perform()
            except AttributeError as er:
                if debug:
                    print("\terror element_send", er)
                try:
                    # This approach should work regardless
                    for key in keys:
                        element.send_keys(key)
                except AttributeError as err:
                    if debug:
                        print("\terror element_send", err)
                    # Be careful with recursive calls - you might want to add a counter to prevent infinite recursion
                    # Also, you're passing keys as a list in the recursive call, which doesn't match the expected *keys
                    # self.element_send(element, keys)
                except StaleElementReferenceException:
                    """N'existe plus"""
            except StaleElementReferenceException:
                """N'existe plus"""

    def send_paste(self, element: WebElement = None):
        """Send Ctrl+V to paste clipboard content into the specified element."""
        self.print(f"Sending paste (Ctrl+V) to element")
        element = ActionChains(self.driver) if element is None else ActionChains(self.driver).move_to_element(element)
        element.key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()

    def close(self):
        """Close the browser."""
        self.driver.quit()
        self.print("Browser closed")

    def move(self, point: Point | int, y=None):
        """Move the browser window to the specified screen coordinates."""
        if y is not None:
            point = Point(point, y)
        self.driver.set_window_position(point.x, point.y)


if __name__ == "__main__":
    browser = SeleniumBrowser(point=Point(0, 0), headless=False)
    try:
        browser.load("https://example.com")  # Replace with a page containing <input type="checkbox">
        checkbox = browser.get_element_attributes("input", 'type="checkbox"')
        if checkbox:
            print(f"Checkbox type: {checkbox.get_attribute('type')}")
            print(f"Attributes: {browser.get_all_attributes(checkbox)}")
        else:
            print("Checkbox not found")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        browser.close()
