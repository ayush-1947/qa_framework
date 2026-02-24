"""
test_donate.py — SNF Donate Form QA Suite
==========================================
TARGET:  https://sfdev.4review.info/donate
SCOPE:   Fill form → click 'Proceed To Pay' → STOP.
         No payment is processed. No Razorpay interaction.

═══════════════════════════════════════════════════════════════════
 WHAT EVERY TEST IN THIS FILE DOES AND DOES NOT DO
═══════════════════════════════════════════════════════════════════
 ✅  Navigate to the donate page
 ✅  Interact with form fields (select amounts, fill text, etc.)
 ✅  Click 'Proceed To Pay'
 ✅  Check the form's OWN validation error messages
 ✅  Check form field attributes (maxlength, CSS, etc.)
 ❌  Never wait for or detect the Razorpay overlay
 ❌  Never interact with Razorpay in any way
 ❌  Never process or simulate any payment

═══════════════════════════════════════════════════════════════════
 WHY THE ORIGINAL TESTS WERE TRIVIALLY PASSING
═══════════════════════════════════════════════════════════════════
 Every negative test asserted:  assert not is_success_modal_displayed()
 The #successDon modal only appears AFTER a real payment completes.
 Since tests stop before payment, the modal NEVER appears — the
 assertion was ALWAYS True regardless of validation working or not.
 Also, the form has novalidate='novalidate' which disables browser
 HTML5 validation — all validation must be done by JS.

 CORRECT assertion for negative tests (used in this file):
   result = donate_page.click_proceed_and_check_validation()
   assert result["error_shown"]    ← a real JS error message appeared
   assert result["form_still_up"]  ← page didn't navigate away
"""

import pytest
from pages.donate_page import DonatePage


# ======================================================================
# TC-001 to TC-005: Page Load & UI
# ======================================================================

class TestPageLoadAndUI:
    """Verify the donate form renders correctly with all required elements."""

    def test_donate_form_is_displayed(self, donate_page):
        """TC-001: Donation form container must be visible after navigation."""
        assert donate_page.is_element_visible(donate_page._DONATE_FORM), \
            "Donation form (#donation) should be visible on the donate page."

    def test_proceed_to_pay_button_is_visible(self, donate_page):
        """TC-002: 'Proceed To Pay' button must be rendered and visible."""
        assert donate_page.is_proceed_button_visible(), \
            "The 'Proceed To Pay' button must be visible to users."

    def test_proceed_button_label(self, donate_page):
        """TC-003: CTA button must display correct label text."""
        text = donate_page.get_proceed_button_text()
        assert "Proceed To Pay" in text, \
            f"Button label mismatch. Found: '{text}'"

    def test_monthly_radio_is_default_selected(self, donate_page):
        """TC-004: 'Donate Monthly' must be pre-selected by default."""
        assert donate_page.is_monthly_selected(), \
            "'Donate Monthly' radio button should be selected by default."

    def test_currency_label_is_INR(self, donate_page):
        """TC-005: All preset amount tabs must display 'INR' as currency."""
        currency = donate_page.get_currency_label()
        assert currency == "INR", \
            f"Currency label should be 'INR', found: '{currency}'"


# ======================================================================
# TC-006 to TC-007: Donation Type Selection
# ======================================================================

class TestDonationTypeSelection:
    """Verify monthly/once radio button behaviour."""

    def test_select_one_time_donation(self, donate_page):
        """TC-006: Switching to 'Donate Once' must deselect 'Donate Monthly'."""
        donate_page.select_one_time_donation()
        assert donate_page.is_once_selected(), \
            "'Donate Once' should be selected after click."
        assert not donate_page.is_monthly_selected(), \
            "'Donate Monthly' must be deselected when 'Donate Once' is chosen."

    def test_switch_back_to_monthly(self, donate_page):
        """TC-007: Switching back from Once to Monthly must work correctly."""
        donate_page.select_one_time_donation()
        donate_page.select_monthly_donation()
        assert donate_page.is_monthly_selected(), \
            "Should be able to switch back to 'Donate Monthly'."


# ======================================================================
# TC-011 to TC-016: Donation Amount Selection
# ======================================================================

class TestAmountSelection:
    """Verify preset and custom donation amount behaviour."""

    @pytest.mark.parametrize("amount_method,expected_value", [
        ("select_amount_300",  "300"),
        ("select_amount_500",  "500"),
        ("select_amount_1000", "1000"),
    ])
    def test_preset_amount_selection(self, donate_page, amount_method, expected_value):
        """TC-011/012/013: Each preset tab must get the 'active' CSS class."""
        getattr(donate_page, amount_method)()
        from selenium.webdriver.common.by import By
        tab_id = {"300": "fifty", "500": "twentyfive", "1000": "fifteen"}[expected_value]
        element = donate_page.find_element((By.XPATH, f"//a[@id='{tab_id}']"))
        assert "active" in element.get_attribute("class"), \
            f"Amount tab for {expected_value} should have 'active' class."

    def test_other_amount_input_appears_on_other_selection(self, donate_page):
        """TC-014: 'Other' input must appear only when 'Other' tab is clicked."""
        assert not donate_page.is_other_amount_input_visible(), \
            "Other amount input should be hidden initially."
        donate_page.select_other_amount()
        assert donate_page.is_other_amount_input_visible(), \
            "Other amount input should appear after clicking 'Other'."

    @pytest.mark.parametrize("custom_amount", ["100", "50000", "1"])
    def test_valid_custom_amounts(self, donate_page, custom_amount):
        """TC-015: Valid custom amounts must be retained in the input field."""
        donate_page.enter_other_amount(custom_amount)
        assert donate_page.get_other_amount_value() == custom_amount, \
            f"Custom amount '{custom_amount}' was not retained."

    @pytest.mark.parametrize("invalid_amount", [
        "-100", "0", "abc",
        "<script>alert('xss')</script>",
        "9" * 20, "1.5.5",
    ])
    def test_invalid_custom_amounts_blocked(self, donate_page, invalid_amount):
        """
        TC-016: Invalid amounts must be caught by JS validation.
        After clicking 'Proceed To Pay' the form's own error message must
        appear AND the form must still be on screen.

        If this FAILS → the form silently passed an invalid amount forward.
        """
        donate_page.enter_other_amount(invalid_amount)
        donate_page.enter_name("Test User")
        donate_page.enter_email("test@example.com")
        donate_page.enter_address("Test Address, Mumbai")
        donate_page.enter_pan("ABCDE1234F")

        # ── Click Proceed To Pay (last in-scope action) ──
        result = donate_page.click_proceed_and_check_validation()

        assert result["form_still_up"], \
            "Donate form should still be on screen after failed validation."
        assert result["error_shown"], (
            f"BUG: No validation error shown for invalid amount '{invalid_amount}'. "
            f"The form's JS did not block this input."
        )


# ======================================================================
# TC-017 to TC-028: Form Field Validation
# ======================================================================

class TestFormFieldValidation:
    """Boundary value, negative, and security validation for all form fields."""

    # ── Name field ────────────────────────────────────────────────────────

    def test_name_field_max_length_attribute(self, donate_page):
        """
        TC-017: Name input must have maxlength='100' set in HTML.
        HTML source confirms: <input id='name' maxlength='100'>
        If FAILS → attribute is missing from HTML — application bug.
        """
        assert donate_page.get_name_max_length() == "100", \
            "BUG: Name field is missing maxlength='100' attribute in HTML."

    def test_name_field_boundary_100_chars(self, donate_page):
        """TC-018: Name field must accept exactly 100 characters."""
        donate_page.enter_name("A" * 100)
        assert len(donate_page.get_name_value()) <= 100, \
            "Name field must not accept more than 100 characters."

    def test_name_field_boundary_101_chars_truncated(self, donate_page):
        """TC-019 (BVA): 101-char input must be truncated to 100 by maxlength."""
        donate_page.enter_name("B" * 101)
        assert len(donate_page.get_name_value()) == 100, \
            "BUG: 101-char name was not truncated to 100 by the maxlength attribute."

    @pytest.mark.parametrize("xss_payload", [
        "<script>alert('XSS')</script>",
        "'; DROP TABLE users; --",
        "javascript:alert(1)",
        "<img src=x onerror=alert(1)>",
    ])
    def test_name_field_xss_and_sql_injection(self, donate_page, xss_payload):
        """TC-020 (Security): Payloads in name field must not trigger JS alerts."""
        donate_page.enter_name(xss_payload)
        try:
            alert = donate_page.driver.switch_to.alert
            alert.dismiss()
            pytest.fail(f"BUG: XSS triggered an alert dialog: '{xss_payload}'")
        except Exception:
            pass  # No alert — this is the expected result

    def test_name_with_special_characters(self, donate_page):
        """TC-021: Apostrophes and hyphens in names must be accepted."""
        donate_page.enter_name("O'Brien Jean-Luc")
        assert donate_page.get_name_value() == "O'Brien Jean-Luc", \
            "Apostrophes and hyphens must be accepted in the name field."

    # ── Email field ───────────────────────────────────────────────────────

    @pytest.mark.parametrize("invalid_email", [
        "notanemail",
        "missing@domain",
        "@nodomain.com",
        "spaces in@email.com",
        "double@@at.com",
        "",
    ])
    def test_invalid_email_formats_rejected(self, donate_page, invalid_email):
        """
        TC-022: Invalid emails must be blocked by JS with a visible error.

        CRITICAL CONTEXT: The form has novalidate='novalidate' — the
        browser's built-in email type checking is completely disabled.
        The form's own JavaScript is responsible for email validation.
        If this FAILS → JS email validation is broken/missing.
        """
        donate_page.fill_valid_form(email=invalid_email)

        # ── Click Proceed To Pay (last in-scope action) ──
        result = donate_page.click_proceed_and_check_validation()

        assert result["form_still_up"], \
            "Form should still be on screen when email validation fails."
        assert result["error_shown"], (
            f"BUG: No error shown for invalid email '{invalid_email}'. "
            f"novalidate is set — JS must validate emails but it is not doing so."
        )

    # ── PAN field ─────────────────────────────────────────────────────────

    @pytest.mark.parametrize("valid_pan", ["ABCPS1234D", "ABCDE1234F"])
    def test_valid_pan_accepted(self, donate_page, valid_pan):
        """TC-023: Valid PANs in AAAAA9999A format must be stored correctly."""
        donate_page.enter_pan(valid_pan)
        assert donate_page.get_pan_value().upper() == valid_pan.upper(), \
            f"Valid PAN '{valid_pan}' was not stored correctly."

    @pytest.mark.parametrize("invalid_pan,description", [
        ("1BCPS1234D",           "Starts with digit"),
        ("ABCPS12345",           "Ends with digit instead of letter"),
        ("ABCPS123",             "Too short (8 chars)"),
        ("ABCPS12345DD",         "Too long"),
        ("abcps1234d",           "Lowercase"),
        ("",                     "Empty PAN"),
        ("<script>xss</script>", "XSS payload in PAN field"),
    ])
    def test_invalid_pan_formats(self, donate_page, invalid_pan, description):
        """
        TC-024: Invalid PAN formats must be blocked by JS validation.
        If FAILS → app accepts invalid PANs, 80G certificates cannot be issued.
        """
        donate_page.fill_valid_form(pan=invalid_pan)

        # ── Click Proceed To Pay (last in-scope action) ──
        result = donate_page.click_proceed_and_check_validation()

        assert result["form_still_up"], \
            f"[{description}] Form should still be on screen after PAN validation failure."
        assert result["error_shown"], (
            f"BUG [{description}]: No error shown for invalid PAN '{invalid_pan}'. "
            f"PAN JS validation is not working."
        )

    def test_pan_field_max_length(self, donate_page):
        """TC-025: PAN field must have maxlength='11' in HTML."""
        assert donate_page.get_pan_max_length() == "11", \
            f"PAN maxlength should be 11. Found: {donate_page.get_pan_max_length()}"

    def test_pan_text_transforms_to_uppercase(self, donate_page):
        """TC-026: PAN field must have CSS text-transform:uppercase."""
        donate_page.enter_pan("abcps1234d")
        css = donate_page.get_css_property(donate_page._PAN_INPUT, "text-transform")
        assert css == "uppercase", \
            "BUG: PAN field is missing CSS 'text-transform: uppercase'."

    # ── Address field ─────────────────────────────────────────────────────

    def test_address_max_length_boundary(self, donate_page):
        """TC-027 (BVA): Address field must accept exactly 200 characters."""
        donate_page.enter_address("A" * 200)
        stored = donate_page.get_attribute(donate_page._ADDRESS_INPUT, "value")
        assert len(stored) <= 200, \
            f"Address must not exceed 200 characters. Stored: {len(stored)}"

    @pytest.mark.parametrize("xss_payload", [
        "<script>alert('XSS')</script>",
        "'; DROP TABLE donors; --",
    ])
    def test_address_xss_injection(self, donate_page, xss_payload):
        """TC-028 (Security): XSS payloads in address must not execute."""
        donate_page.enter_address(xss_payload)
        try:
            alert = donate_page.driver.switch_to.alert
            alert.dismiss()
            pytest.fail(f"BUG: XSS executed in address field: '{xss_payload}'")
        except Exception:
            pass


# ======================================================================
# TC-029 to TC-033: Mandatory Field Validation
# ======================================================================

class TestMandatoryFieldValidation:
    """Verify required fields are enforced when form is submitted."""

    @pytest.mark.parametrize("missing_field,fill_kwargs", [
        ("name",    {"name": ""}),
        ("email",   {"email": ""}),
        ("address", {"address": ""}),
        ("pan",     {"pan": ""}),
    ])
    def test_submit_with_missing_required_field(
        self, donate_page, missing_field, fill_kwargs
    ):
        """
        TC-029-032: Submitting with a blank required field must show an error.

        CRITICAL CONTEXT: novalidate='novalidate' disables the browser's
        'required' attribute enforcement. The form's JS must check required
        fields. If FAILS → users can submit to payment with empty fields.
        """
        donate_page.fill_valid_form(**fill_kwargs)

        # ── Click Proceed To Pay (last in-scope action) ──
        result = donate_page.click_proceed_and_check_validation()

        assert result["form_still_up"], \
            f"Form should remain visible when '{missing_field}' is blank."
        assert result["error_shown"], (
            f"BUG: No error shown when required field '{missing_field}' was blank. "
            f"JS required-field validation is missing."
        )

    def test_submit_completely_empty_form(self, donate_page):
        """TC-033: Completely empty form must show errors on submission."""
        # ── Click Proceed To Pay (last in-scope action) ──
        result = donate_page.click_proceed_and_check_validation()

        assert result["form_still_up"], \
            "Form should still be visible after empty submit attempt."
        assert result["error_shown"], \
            "BUG: No errors shown for completely empty form submission."


# ======================================================================
# TC-034 to TC-035: Inspiration Dropdown
# ======================================================================

class TestInspirationDropdown:
    """Verify the 'What inspired you to give today?' dropdown."""

    @pytest.mark.parametrize("option", [
        "Sanctuary Nature Foundation website",
        "Sanctuary Asia magazine",
        "Sanctuary Cub magazine",
        "Newsletter",
        "Someone I know",
        "Sanctuary social media",
    ])
    def test_all_inspiration_options_selectable(self, donate_page, option):
        """TC-034: All six dropdown options must be selectable."""
        donate_page.select_inspiration(option)
        assert donate_page.get_selected_inspiration() == option, \
            f"Could not select '{option}' from dropdown."

    def test_default_inspiration_option(self, donate_page):
        """TC-035: Default must be 'Sanctuary Nature Foundation website'."""
        assert donate_page.get_selected_inspiration() == \
            "Sanctuary Nature Foundation website", \
            f"Default inspiration incorrect. Got: '{donate_page.get_selected_inspiration()}'"


# ======================================================================
# TC-037 to TC-038: Mobile Field
# ======================================================================

class TestMobileField:
    """Mobile is optional but must validate format when provided."""

    @pytest.mark.parametrize("mobile", ["9876543210", "0987654321", ""])
    def test_valid_mobile_numbers(self, donate_page, mobile):
        """TC-037: Valid and empty mobile numbers must be accepted by the field."""
        donate_page.fill_valid_form()
        donate_page.enter_mobile(mobile)
        stored = donate_page.get_attribute(donate_page._MOBILE_INPUT, "value")
        assert stored == mobile, \
            f"Mobile '{mobile}' was not retained. Got: '{stored}'"

    @pytest.mark.parametrize("invalid_mobile", [
        "abcdefghij",
        "12345",
        "+91-98765-43210-extra",
    ])
    def test_invalid_mobile_format_on_submit(self, donate_page, invalid_mobile):
        """
        TC-038: Invalid mobile must be blocked by JS validation with an error.
        If FAILS → invalid mobile numbers pass through to the payment gateway.
        """
        donate_page.fill_valid_form()
        donate_page.enter_mobile(invalid_mobile)

        # ── Click Proceed To Pay (last in-scope action) ──
        result = donate_page.click_proceed_and_check_validation()

        assert result["form_still_up"], \
            f"Form should remain visible for invalid mobile '{invalid_mobile}'."
        assert result["error_shown"], (
            f"BUG: No error shown for invalid mobile '{invalid_mobile}'. "
            f"Mobile field JS validation is not working."
        )


# ======================================================================
# TC-040: Happy Path — End-to-End (stops at button click)
# ======================================================================

class TestHappyPath:
    """
    Full valid-form submission ending at 'Proceed To Pay' click.
    This is the EXACT scope boundary — click the button, then stop.
    """

    @pytest.mark.parametrize("donation_type,amount", [
        ("monthly", "300"),
        ("monthly", "500"),
        ("monthly", "1000"),
        ("once",    "300"),
        ("once",    "500"),
        ("once",    "1000"),
        ("monthly", "2500"),
        ("once",    "10000"),
    ])
    def test_happy_path_valid_submission(self, donate_page, donation_type, amount):
        """
        TC-040: Fill the form with valid data, verify all fields, then click
        'Proceed To Pay'. Test ends immediately after the click.

        SCOPE:
          ✅  Verify field values are correctly set before submission
          ✅  Verify 'Proceed To Pay' button is visible and clickable
          ✅  Click 'Proceed To Pay'
          ✅  Verify NO validation errors appeared (valid data was accepted)
          ❌  Do NOT check whether Razorpay opened
          ❌  Do NOT interact with Razorpay
          ❌  Do NOT process any payment
        """
        donate_page.fill_valid_form(
            name="Priya Nair",
            email="priya.nair@conserve.in",
            mobile="9123456780",
            address="7 Forest Lane, Bangalore, Karnataka 560001",
            pan="BCDEF2345G",
            amount_type=amount,
            donation_type=donation_type,
        )

        # Verify the form was filled correctly before clicking
        assert donate_page.get_name_value() == "Priya Nair", \
            "Name field was not filled correctly."
        assert donate_page.get_pan_value().upper() == "BCDEF2345G", \
            "PAN field was not filled correctly."
        assert donate_page.is_proceed_button_visible(), \
            "Proceed To Pay button must be visible and accessible."

        # ── FINAL IN-SCOPE ACTION: Click 'Proceed To Pay' ──────────────────
        result = donate_page.click_proceed_and_check_validation()
        # ───────────────────────────────────────────────────────────────────

        # For valid data: the form must NOT show any validation errors
        assert not result["error_shown"], (
            f"BUG: A validation error appeared for perfectly valid input "
            f"(type={donation_type}, amount={amount}). "
            f"Error: '{result['error_text']}'"
        )

        #   TEST ENDS HERE. Nothing beyond this line touches the payment gateway.