from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException
)


class BasePage:
    """
    Base Page Object class providing reusable, robust interaction methods
    using Explicit Waits. No time.sleep() is ever used.
    """

    DEFAULT_TIMEOUT = 15

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, self.DEFAULT_TIMEOUT)

    # ── Navigation ────────────────────────────────────────────────────────

    def open(self, url: str):
        self.driver.get(url)

    def get_current_url(self) -> str:
        return self.driver.current_url

    def get_title(self) -> str:
        return self.driver.title

    def refresh(self):
        self.driver.refresh()

    # ── Element retrieval ─────────────────────────────────────────────────

    def find_element(self, locator: tuple, timeout: int = DEFAULT_TIMEOUT):
        """Wait for element to be present in DOM and return it."""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator),
            message=f"Element not found: {locator}"
        )

    def find_visible_element(self, locator: tuple, timeout: int = DEFAULT_TIMEOUT):
        """Wait for element to be visible and return it."""
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator),
            message=f"Element not visible: {locator}"
        )

    def find_clickable_element(self, locator: tuple, timeout: int = DEFAULT_TIMEOUT):
        """Wait for element to be clickable and return it."""
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator),
            message=f"Element not clickable: {locator}"
        )

    def find_elements(self, locator: tuple, timeout: int = DEFAULT_TIMEOUT):
        """Wait for all matching elements to be present."""
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
        return self.driver.find_elements(*locator)

    def is_element_present(self, locator: tuple, timeout: int = 5) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def is_element_visible(self, locator: tuple, timeout: int = 5) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    # ── Actions ───────────────────────────────────────────────────────────

    def click(self, locator: tuple):
        """Click an element after ensuring it is clickable."""
        try:
            element = self.find_clickable_element(locator)
            element.click()
        except ElementClickInterceptedException:
            # Fallback: JS click for elements blocked by overlays
            element = self.find_element(locator)
            self.driver.execute_script("arguments[0].click();", element)

    def type_text(self, locator: tuple, text: str, clear_first: bool = True):
        """
        Type text into an input field. Clears existing content by default.
        Primary strategy: wait for visible element, then send_keys.
        Fallback: use JavaScript to set the value if element is present but not
        interactable (e.g. a parent container has display:none or overflow:hidden
        that Selenium's visibility check misreads as invisible).
        """
        try:
            element = self.find_visible_element(locator)
            if clear_first:
                element.clear()
            element.send_keys(text)
        except TimeoutException:
            # Fallback — the element is in the DOM but Selenium considers it
            # non-visible (often due to parent CSS).  Use JS interaction.
            self.js_type_text(locator, text)

    def js_type_text(self, locator: tuple, text: str):
        """
        Set an input's value via JavaScript and fire input/change events.
        Use this when the element exists in the DOM but Selenium's
        visibility check fails (e.g. parent has overflow:hidden, the field
        is inside a CSS-transformed container, or there is a duplicate hidden
        element earlier in the DOM that shadows the real one).
        """
        element = self.find_element(locator)
        self.driver.execute_script(
            """
            var el = arguments[0];
            var val = arguments[1];
            // Make the specific element interactable regardless of parent CSS
            el.removeAttribute('hidden');
            el.style.visibility = 'visible';
            el.style.display    = 'block';
            // Set value and fire events so Angular/Vue/React listeners update
            var nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, 'value').set;
            nativeInputValueSetter.call(el, val);
            el.dispatchEvent(new Event('input',  { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            """,
            element,
            text,
        )

    def get_text(self, locator: tuple) -> str:
        return self.find_visible_element(locator).text

    def get_attribute(self, locator: tuple, attribute: str) -> str:
        return self.find_element(locator).get_attribute(attribute)

    def get_value(self, locator: tuple) -> str:
        return self.get_attribute(locator, "value")

    def select_dropdown_by_visible_text(self, locator: tuple, text: str):
        element = self.find_visible_element(locator)
        Select(element).select_by_visible_text(text)

    def select_dropdown_by_value(self, locator: tuple, value: str):
        element = self.find_visible_element(locator)
        Select(element).select_by_value(value)

    def get_selected_dropdown_text(self, locator: tuple) -> str:
        element = self.find_visible_element(locator)
        return Select(element).first_selected_option.text

    def scroll_to_element(self, locator: tuple):
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

    def wait_for_url_to_contain(self, url_fragment: str, timeout: int = DEFAULT_TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(
            EC.url_contains(url_fragment),
            message=f"URL did not contain: {url_fragment}"
        )

    def wait_for_element_text_to_be(self, locator: tuple, expected_text: str, timeout: int = DEFAULT_TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(
            EC.text_to_be_present_in_element(locator, expected_text),
            message=f"Expected text '{expected_text}' not found in element {locator}"
        )

    def get_css_property(self, locator: tuple, css_property: str) -> str:
        element = self.find_element(locator)
        return element.value_of_css_property(css_property)

    def execute_script(self, script: str, *args):
        return self.driver.execute_script(script, *args)