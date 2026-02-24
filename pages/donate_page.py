"""
donate_page.py
==============
Page Object for the SNF Donate form at sfdev.4review.info/donate

SCOPE BOUNDARY (hard constraint):
  Tests execute UP TO AND INCLUDING clicking 'Proceed To Pay'.
  This file deliberately contains NO code to detect, wait for,
  or interact with the Razorpay payment gateway in any way.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time

from pages.base_page import BasePage


class DonatePage(BasePage):

    # ── Locators ──────────────────────────────────────────────────────────
    #
    # WHY SCOPED CSS SELECTORS for form fields:
    # The page has multiple forms (nav, newsletter, razorpay hidden form).
    # Several share generic ids like "name" and "email" on hidden inputs.
    # By.ID returns the FIRST DOM match — often the wrong hidden element.
    # Scoping to "#donation" guarantees we hit the visible donation field.
    # ─────────────────────────────────────────────────────────────────────

    _DONATE_NAV_LINK    = (By.XPATH, "//a[contains(translate(text(),'donate','DONATE'),'DONATE') or contains(@href,'donate')]")
    _DONATE_FORM        = (By.ID, "donation")

    _RADIO_MONTHLY      = (By.ID, "monthly")
    _RADIO_ONCE         = (By.ID, "once")

    _AMOUNT_300         = (By.ID, "fifty")
    _AMOUNT_500         = (By.ID, "twentyfive")
    _AMOUNT_1000        = (By.ID, "fifteen")
    _AMOUNT_OTHER       = (By.ID, "otheroption")
    _OTHER_AMOUNT_INPUT = (By.ID, "otheramount")

    _INSPIRED_DROPDOWN  = (By.ID, "inspired_option")

    # Form inputs scoped to #donation to avoid shadow matches
    _NAME_INPUT    = (By.CSS_SELECTOR, "#donation #name")
    _EMAIL_INPUT   = (By.CSS_SELECTOR, "#donation #email")
    _MOBILE_INPUT  = (By.CSS_SELECTOR, "#donation #mobile")
    _ADDRESS_INPUT = (By.CSS_SELECTOR, "#donation #address")
    _PAN_INPUT     = (By.CSS_SELECTOR, "#donation #pan")

    _PROCEED_TO_PAY_BTN = (By.ID, "pay_button")

    # Validation error elements
    # .common-error  → submit-level error banner shown by the form's JS
    # .error          → per-field error divs inside each .form-group
    _COMMON_ERROR     = (By.CSS_SELECTOR, ".common-error")
    _ALL_FIELD_ERRORS = (By.CSS_SELECTOR, "#donation .form-group .error")

    _CURRENCY_SPANS   = (By.CSS_SELECTOR, "span.currency")

    # ── Navigation ────────────────────────────────────────────────────────

    def navigate_to_donate(self, base_url: str):
        self.open(base_url)
        self.click(self._DONATE_NAV_LINK)
        self.wait_for_donate_form_to_load()

    def wait_for_donate_form_to_load(self):
        """Wait for #donation form to be in view."""
        element = self.find_element(self._DONATE_FORM)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'start', behavior: 'instant'});",
            element,
        )
        self.find_visible_element(self._DONATE_FORM)

    # ── Scroll helper ─────────────────────────────────────────────────────

    def _scroll_to(self, locator):
        try:
            el = self.find_element(locator)
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});",
                el,
            )
        except Exception:
            pass

    # ── Donation type ─────────────────────────────────────────────────────

    def select_monthly_donation(self):
        self._scroll_to(self._RADIO_MONTHLY)
        self.click(self._RADIO_MONTHLY)

    def select_one_time_donation(self):
        self._scroll_to(self._RADIO_ONCE)
        self.click(self._RADIO_ONCE)

    def is_monthly_selected(self) -> bool:
        return self.find_element(self._RADIO_MONTHLY).is_selected()

    def is_once_selected(self) -> bool:
        return self.find_element(self._RADIO_ONCE).is_selected()

    # ── Amount selection ──────────────────────────────────────────────────

    def select_amount_300(self):
        self._scroll_to(self._AMOUNT_300)
        self.click(self._AMOUNT_300)

    def select_amount_500(self):
        self._scroll_to(self._AMOUNT_500)
        self.click(self._AMOUNT_500)

    def select_amount_1000(self):
        self._scroll_to(self._AMOUNT_1000)
        self.click(self._AMOUNT_1000)

    def select_other_amount(self):
        self._scroll_to(self._AMOUNT_OTHER)
        self.click(self._AMOUNT_OTHER)

    def enter_other_amount(self, amount: str):
        self.select_other_amount()
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self._OTHER_AMOUNT_INPUT)
        )
        self._scroll_to(self._OTHER_AMOUNT_INPUT)
        self.type_text(self._OTHER_AMOUNT_INPUT, amount)

    def get_other_amount_value(self) -> str:
        return self.get_value(self._OTHER_AMOUNT_INPUT)

    def is_other_amount_input_visible(self) -> bool:
        return self.is_element_visible(self._OTHER_AMOUNT_INPUT)

    def get_currency_label(self) -> str:
        elements = self.find_elements(self._CURRENCY_SPANS)
        return elements[0].text.strip() if elements else ""

    # ── Inspiration dropdown ──────────────────────────────────────────────

    def select_inspiration(self, visible_text: str):
        self._scroll_to(self._INSPIRED_DROPDOWN)
        self.select_dropdown_by_visible_text(self._INSPIRED_DROPDOWN, visible_text)

    def get_selected_inspiration(self) -> str:
        return self.get_selected_dropdown_text(self._INSPIRED_DROPDOWN)

    # ── Form fields ───────────────────────────────────────────────────────

    def enter_name(self, name: str):
        self._scroll_to(self._NAME_INPUT)
        self.type_text(self._NAME_INPUT, name)

    def enter_email(self, email: str):
        self._scroll_to(self._EMAIL_INPUT)
        self.type_text(self._EMAIL_INPUT, email)

    def enter_mobile(self, mobile: str):
        self._scroll_to(self._MOBILE_INPUT)
        self.type_text(self._MOBILE_INPUT, mobile)

    def enter_address(self, address: str):
        self._scroll_to(self._ADDRESS_INPUT)
        self.type_text(self._ADDRESS_INPUT, address)

    def enter_pan(self, pan: str):
        self._scroll_to(self._PAN_INPUT)
        self.type_text(self._PAN_INPUT, pan)

    # ── Getters ───────────────────────────────────────────────────────────

    def get_name_value(self) -> str:
        return self.get_value(self._NAME_INPUT)

    def get_email_value(self) -> str:
        return self.get_value(self._EMAIL_INPUT)

    def get_pan_value(self) -> str:
        return self.get_value(self._PAN_INPUT)

    def get_name_max_length(self) -> str:
        return self.get_attribute(self._NAME_INPUT, "maxlength")

    def get_address_max_length(self) -> str:
        return self.get_attribute(self._ADDRESS_INPUT, "maxlength")

    def get_pan_max_length(self) -> str:
        return self.get_attribute(self._PAN_INPUT, "maxlength")

    # ── Validation error helpers ──────────────────────────────────────────
    #
    # These helpers check only the FORM's own error UI — the .common-error
    # banner and per-field .error divs rendered by the form's JavaScript.
    # They have nothing to do with the payment gateway.
    # ─────────────────────────────────────────────────────────────────────

    def get_common_error_text(self) -> str:
        """Return text of the .common-error element, or '' if not visible."""
        if self.is_element_visible(self._COMMON_ERROR, timeout=5):
            return self.get_text(self._COMMON_ERROR).strip()
        return ""

    def get_all_field_error_texts(self) -> list:
        """Return list of all non-empty per-field error messages."""
        try:
            elements = self.find_elements(self._ALL_FIELD_ERRORS, timeout=5)
            return [el.text.strip() for el in elements if el.text.strip()]
        except Exception:
            return []

    def is_any_error_displayed(self, timeout: int = 5) -> bool:
        """True if any form validation error is currently visible."""
        if self.is_element_visible(self._COMMON_ERROR, timeout=timeout):
            if self.get_text(self._COMMON_ERROR).strip():
                return True
        return len(self.get_all_field_error_texts()) > 0

    def is_donation_form_still_visible(self) -> bool:
        """True if the #donation form is still on screen (no navigation occurred)."""
        return self.is_element_visible(self._DONATE_FORM, timeout=5)

    # ── Submission ────────────────────────────────────────────────────────

    def click_proceed_to_pay(self):
        """
        Click the 'Proceed To Pay' button. This is the FINAL action in scope.
        After this call, tests must not take any further action that touches
        the payment gateway.
        """
        self._scroll_to(self._PROCEED_TO_PAY_BTN)
        self.click(self._PROCEED_TO_PAY_BTN)

    def click_proceed_and_check_validation(self) -> dict:
        """
        Click 'Proceed To Pay' then immediately check ONLY the form's own
        validation feedback (error messages and form visibility).

        Used in negative tests to confirm that bad input was BLOCKED
        by the form's own JS validation before reaching the gateway.

        Returns:
          error_shown   (bool) — True = validation error message appeared
          error_text    (str)  — the .common-error message text (if any)
          form_still_up (bool) — True = still on the form page (not navigated)

        NOTE: This method deliberately does NOT check whether the Razorpay
        gateway opened. That would go beyond the test scope boundary.
        Blocking is inferred from: error_shown=True + form_still_up=True.
        """
        self.click_proceed_to_pay()
        time.sleep(1)   # allow form JS validation to run and render errors
        return {
            "error_shown":   self.is_any_error_displayed(timeout=4),
            "error_text":    self.get_common_error_text(),
            "form_still_up": self.is_donation_form_still_visible(),
        }

    # ── Button helpers ────────────────────────────────────────────────────

    def get_proceed_button_text(self) -> str:
        return self.get_text(self._PROCEED_TO_PAY_BTN)

    def is_proceed_button_visible(self) -> bool:
        return self.is_element_visible(self._PROCEED_TO_PAY_BTN)

    # ── Composite fill method ─────────────────────────────────────────────

    def fill_valid_form(
        self,
        name: str          = "Ananya Sharma",
        email: str         = "ananya.sharma@example.com",
        mobile: str        = "9876543210",
        address: str       = "12 Banyan Marg, Pune, Maharashtra 411001",
        pan: str           = "ABCPS1234D",
        amount_type: str   = "300",
        donation_type: str = "monthly",
    ):
        if donation_type.lower() == "monthly":
            self.select_monthly_donation()
        else:
            self.select_one_time_donation()

        amount_map = {
            "300":  self.select_amount_300,
            "500":  self.select_amount_500,
            "1000": self.select_amount_1000,
        }
        if amount_type in amount_map:
            amount_map[amount_type]()
        else:
            self.enter_other_amount(amount_type)

        self.enter_name(name)
        self.enter_email(email)
        self.enter_mobile(mobile)
        self.enter_address(address)
        self.enter_pan(pan)