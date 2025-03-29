import os
from functools import wraps
from time import sleep

import playwright

from Classes import Point
from Times import elapsed_seconds, now


def profile_name(profile: str):
    start = profile.rindex(os.path.sep)
    name = profile[start + len(os.path.sep):]
    return name


from playwright.sync_api import Page, Locator, BrowserContext, sync_playwright
from typing import Optional


def retry_on_network_disconnect(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        while True:
            try:
                return func(self, *args, **kwargs)
            except (playwright._impl._errors.Error, playwright._impl._errors.TimeoutError) as e:
                self.print("Network problem, retrying in 30 seconds...", str(e))
                sleep(30)

    return wrapper


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def get_locator_text(locator, timeout=1000):
    try:
        return locator.text_content(timeout=timeout)
    except playwright._impl._errors.TimeoutError:
        return ""


class PlaywrightBrowser:
    def __init__(self, point=None, profile=None, headless=False, debug=True):
        self.point = point
        if point is None:
            self.point = Point(0, 0)
        self.profile: str = profile
        self.headless: bool = headless
        self.context: BrowserContext = None
        self.pages = []
        self.name: Optional[str] = None
        self.working_window_num: int = 0
        self.windows_url: list[str] = [""]
        self.playwright = None
        self.debug = debug
        self.set_browser(profile)

    def set_browser(self, profile=None):
        if profile is not None:
            self.profile = profile
        self.playwright = sync_playwright().start()
        browser_type = self.playwright.chromium  # Change to firefox or webkit if needed
        args = ["--disable-blink-features=AutomationControlled"]
        if self.profile:
            args.append(f'--user-data-dir={self.profile}')
        args.append(f'--window-position={self.point.x},{self.point.y}')
        self.context = browser_type.launch_persistent_context(
            user_data_dir=self.profile,
            headless=self.headless,
            args=[arg for arg in args if not arg.startswith('--user-data-dir')]
        )
        self.pages = list(self.context.pages)
        first_page = self.pages[0]
        first_page.set_viewport_size({"width": 1920, "height": 1080})

    @retry_on_network_disconnect
    def load(self, url, window_index=None):
        window_index = self.working_window_num if window_index is None else window_index
        assert 0 <= window_index < len(self.pages)
        self.windows_url[window_index] = url
        self.pages[window_index].goto(url)
        self.print(f"{url} loaded in window {window_index}")

    @retry_on_network_disconnect
    def goto(self, url=None, tab_index=None):
        tab_index = self.working_window_num if tab_index is None else tab_index
        assert 0 <= tab_index < len(self.pages)
        self.pages[tab_index].bring_to_front()
        self.print(f"Navigated to {tab_index} tab")
        if url:
            self.load(url, tab_index)

    @retry_on_network_disconnect
    def new_page(self, url=None, wait_load=False) -> Page:
        new_page = self.context.new_page()
        self.pages.append(new_page)
        if url:
            self.windows_url.append(url)
            new_page.goto(url)
        self.working_window_num = len(self.pages) - 1
        if wait_load:
            new_page.wait_for_load_state()
        self.print(f"Opened new page with URL: {url}")
        return self.pages[-1]

    @retry_on_network_disconnect
    def refresh(self, page_num=None, goto=None, locator=None) -> bool:
        page = self.get_working_page() if page_num is None else self.pages[page_num]
        if goto:
            self.goto(tab_index=page_num)
        page.reload()
        if locator:
            return wait_element(locator)

    def print(self, message):
        print(f"{now()} {message}")

    def get_working_page(self) -> Page:
        """Returns the current working page object."""
        return self.pages[self.working_window_num]

    def close(self):
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()

    def wait_to_close(self):
        input("Press Enter to close the browser...")
        self.close()

    def get_all_attributes(self, locator: Locator) -> Optional[dict]:
        if locator.count() == 0:
            return None
        all_attributes = locator.evaluate("element => Array.from(element.attributes).reduce((acc, attr) => { acc[attr.name] = attr.value; return acc; }, {})")
        self.print(f"Retrieved {len(all_attributes)} attributes")
        return all_attributes

    def get_locator(self, selector: str, loc: Locator = None) -> Locator:
        """ self.get_locator(".login-button")
        <button class="login-button">Login</button> """
        element = loc if loc else self.get_working_page()
        return element.locator(selector)

    def get_locator_class(self, selector: str, loc: Locator = None) -> Locator:
        """ self.get_locator("login-button")
        <button class="login-button">Login</button> """
        element = loc if loc else self.get_working_page()
        return element.locator("." + selector)

    def get_locator_xpath(self, xpath: str, loc: Locator = None) -> Locator:
        """ self.get_locator_xpath("//div[@id='main']")
        <div id="main">Content</div> """
        return self.get_locator(f"xpath={xpath}", loc)

    def get_locator_text(self, text: str, exact: bool = False, loc: Locator = None) -> Locator:
        """ self.get_locator_text("Click me", exact=True)
        <button>Click me</button> """
        element = loc if loc else self.get_working_page()
        return element.get_by_text(text, exact=exact)

    def get_locator_role(self, role: str, loc: Locator = None, **attributes) -> Locator:
        """ self.get_locator_role("button", name="Submit", disabled=False)
        <button aria-label="Submit">Submit</button> """
        element = loc if loc else self.get_working_page()
        return element.get_by_role(role, **attributes)

    def get_locator_label(self, label: str, exact: bool = False, loc: Locator = None) -> Locator:
        """ self.get_locator_label("Username", exact=True)
        <label>Username<input type="text"></label> """
        element = loc if loc else self.get_working_page()
        return element.get_by_label(label, exact=exact)

    def get_locator_placeholder(self, placeholder: str, exact: bool = False, loc: Locator = None) -> Locator:
        """ self.get_locator_placeholder("Search", exact=True)
        <input placeholder="Search"> """
        element = loc if loc else self.get_working_page()
        return element.get_by_placeholder(placeholder, exact=exact)

    def get_locator_alt_text(self, alt_text: str, exact: bool = False, loc: Locator = None) -> Locator:
        """ self.get_locator_alt_text("Company Logo", exact=True)
        <img alt="Company Logo" src="logo.png"> """
        element = loc if loc else self.get_working_page()
        return element.get_by_alt_text(alt_text, exact=exact)

    def get_locator_title(self, title: str, exact: bool = False, loc: Locator = None) -> Locator:
        """ self.get_locator_title("Help Tooltip", exact=True)
        <span title="Help Tooltip">?</span> """
        element = loc if loc else self.get_working_page()
        return element.get_by_title(title, exact=exact)

    def get_locator_test_id(self, test_id: str, loc: Locator = None) -> Locator:
        """ self.get_locator_test_id("login-form")
        <form data-testid="login-form"></form> """
        element = loc if loc else self.get_working_page()
        return element.get_by_test_id(test_id)

    def get_locators(self, locator: Locator = None, id_: Optional[str] = None, text: Optional[str] = None, xpath: Optional[str] = None,
                     role: Optional[str] = None,
                     label: Optional[str] = None, placeholder: Optional[str] = None, alt_text: Optional[str] = None, title: Optional[str] = None,
                     test_id: Optional[str] = None, class_name: Optional[str] = None, style: Optional[str] = None, exact: bool = False,
                     wait_results=False, **role_attributes
                     ) -> list[Locator]:
        """Locates all elements where ALL provided criteria must match (AND condition).

        Args:
            id_: CSS ID selector (e.g., "main").
            text: Visible text content (e.g., "Click me").
            xpath: XPath expression (e.g., "//div[@id='main']").
            role: ARIA role (e.g., "button").
            label: Label text (e.g., "Username").
            placeholder: Placeholder text (e.g., "Search").
            alt_text: Alt text (e.g., "Company Logo").
            title: Title attribute (e.g., "Help").
            test_id: Test ID (e.g., "login-form").
            class_name: CSS class name (e.g., "css-175oi2r").
            style: Exact style attribute (e.g., "transform: translateY(0px);").
            exact: If True, text-based matches (text, label, etc.) are exact.
            locator: Starting Locator to search within (defaults to entire page).
            wait_results:
            **role_attributes: Additional attributes for role (e.g., name="Submit").

        Returns:
            A list of Locator objects matching all provided criteria.

        Example:
            locators = self.get_specific_locators(class_name="css-175oi2r", test_id="cellInnerDiv", style="transform: translateY(0px); position: absolute; width: 100%;")
            # Matches all <div class="css-175oi2r" data-testid="cellInnerDiv" style="transform: translateY(0px); position: absolute; width: 100%;">
        """
        # Check if at least one criterion is provided
        criteria = {
            "id": id_, "text": text, "xpath": xpath, "role": role, "label": label,
            "placeholder": placeholder, "alt_text": alt_text, "title": title,
            "test_id": test_id, "class_name": class_name, "style": style
        }
        if not any(criteria.values()):
            raise ValueError("At least one criterion must be provided")

        # Start with the provided locator or the entire page
        locator = locator if locator else self.get_working_page()

        # Apply direct selectors for attributes
        selector_parts = []
        if id_:
            selector_parts.append(f"#{id_}")
            # self.print(f"Added id: {id_}", False)
        if test_id:
            selector_parts.append(f"[data-testid='{test_id}']")
            # self.print(f"Added test_id: {test_id}", False)
        if class_name:
            selector_parts.append(f".{class_name}")
            # self.print(f"Added class_name: {class_name}", False)
        if style:
            selector_parts.append(f'[style="{style}"]')
            # self.print(f"Added style: {style}", False)
        if selector_parts:
            combined_selector = "".join(selector_parts)
            locator = locator.locator(combined_selector)
            # self.print(f"Applied combined selector: {combined_selector}", False)
            # Apply XPath separately if provided (XPath can't be combined with CSS directly)
        if xpath:
            locator = locator.locator(f"xpath={xpath}")
            # self.print(f"Applied xpath: {xpath}", False)
        # Apply filters for content-based criteria
        if text:
            locator = locator.filter(has=self.get_locator_text(text, exact=exact, loc=locator))
            # self.print(f"Filtered by text: {text}", False)
        if role:
            locator = locator.filter(has=self.get_locator_role(role, loc=locator, **role_attributes))
            # self.print(f"Filtered by role: {role}", False)
        if label:
            locator = locator.filter(has=self.get_locator_label(label, exact=exact, loc=locator))
            # self.print(f"Filtered by label: {label}", False)
        if placeholder:
            locator = locator.filter(has=self.get_locator_placeholder(placeholder, exact=exact, loc=locator))
            # self.print(f"Filtered by placeholder: {placeholder}", False)
        if alt_text:
            locator = locator.filter(has=self.get_locator_alt_text(alt_text, exact=exact, loc=locator))
            # self.print(f"Filtered by alt_text: {alt_text}", False)
        if title:
            locator = locator.filter(has=self.get_locator_title(title, exact=exact, loc=locator))
            # self.print(f"Filtered by title: {title}", False)

        start = now()
        matches = locator.all()
        count = len(matches)
        if count == 0:
            self.print("No elements found")
        while wait_results and count == 0:
            matches = locator.all()
            count = len(matches)
            sleep(0.1)
        else:
            self.print(f"Found {count} elements {elapsed_seconds(start)}s loaded")
        return matches


def scrap_tweets(account):
    browser = PlaywrightBrowser(point=Point(0, 0), headless=True, profile=f"{profiles_dir}\default")
    # url_2 = "https://x.com/REVpresents"
    url = f"https://x.com/{account}"
    tweets_xpath = r"/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[3]/div/div/section/div/div"
    xpath_loc = browser.get_locator_xpath(tweets_xpath)
    locators: list[Locator] = browser.get_locators(xpath_loc, class_name="css-175oi2r", test_id="cellInnerDiv", wait_results=False)
    texts = [loc.text_content() for loc in locators]
    return texts


def wait_element(locator: Optional[Locator] = None, page: Optional[Page] = None, selector: Optional[str] = None, timeout: int = 5000) -> bool:
    assert locator or (page and selector)
    try:
        if locator:
            locator.wait_for(state="visible", timeout=timeout)
            return True
        else:
            page.wait_for_selector(selector, state="visible", timeout=timeout)
            return True
    except playwright._impl._errors.TimeoutError:
        return False


if __name__ == "__main__":
    profiles_dir = os.getenv("BROWSER_PROFILES")
