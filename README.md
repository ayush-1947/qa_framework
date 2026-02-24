# Sanctuary Nature Foundation — Donate Form QA Automation Framework

**Project:** Selenium + Pytest automation suite for the SNF Donate Form module  
**Target URL:** `https://sfdev.4review.info/magazine` → DONATE  
**Constraint:** Tests must strictly stop before payment processing. No actual payments are processed, and there is no interaction with the Razorpay API.

---

##  Architecture: Page Object Model (POM)
The framework follows strict Page Object Model design patterns to separate test logic from page mechanics.

```text
test_donate.py (Test Logic & Assertions)
      ↓
donate_page.py (Locators & Page Interactions)
      ↓
base_page.py (Selenium Wrappers & Explicit Waits)

```

### Key Principles

* **Explicit Waits Only:** Relies on `WebDriverWait`; no hardcoded `time.sleep()`.
* **Abstraction:** The test layer (`test_donate.py`) contains zero direct Selenium WebDriver calls.
* **Reusable Methods:** Actions are wrapped in composite methods (e.g., `fill_valid_form()`).
* **Parametrized Data:** Uses `@pytest.mark.parametrize` to execute 74 data permutations efficiently.
* **Stable Locators:** Prioritizes `id` and semantic structure over fragile XPaths.

---

##  Project Structure

```text
sanctuary_qa/
├── conftest.py                # Pytest fixtures and WebDriver setup
├── pytest.ini                 # Pytest configuration and defaults
├── requirements.txt           # Python dependencies
├── README.md
│
├── pages/
│   ├── __init__.py
│   ├── base_page.py           # Core Selenium wrapper methods
│   └── donate_page.py         # SNF Donate Form locators and methods
│
├── tests/
│   ├── __init__.py
│   └── test_donate.py         # Pytest execution scripts
│
├── reports/
│   └── report.html            # Auto-generated pytest-html dashboard
│
└── SNF_Donate_QA_Report.xlsx  # Manual Test Cases & Defect Log

```

---

## Quick Start (Windows)

### 1. Prerequisites

* Python 3.9+
* Google Chrome (latest)
* `pip`

### 2. Unzip and Navigate

```bash
unzip sanctuary_qa.zip -d sanctuary_qa
cd sanctuary_qa

```

### 3. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate

```

### 4. Install Dependencies

```bash
pip install -r requirements.txt

```

*Note: ChromeDriver is managed automatically via `webdriver-manager`.*

---

##  Running the Tests

**Run All Tests:**

```bash
pytest

```

**Run in Headless Mode:**

```bash
pytest --headless

```

**Run Specific Test Class:**

```bash
pytest tests/test_donate.py::TestHappyPath -v

```

**Run by Keyword (e.g., testing XSS or PAN validation):**

```bash
pytest -k "xss" -v
pytest -k "pan" -v
pytest -k "boundary" -v

```

**Run with Custom Base URL:**

```bash
pytest --base-url="[https://sfdev.4review.info/magazine](https://sfdev.4review.info/magazine)"

```

**Run in Parallel (requires `pytest-xdist`):**

```bash
pytest -n 4

```

---

## HTML Report & Defect Summary

A visual HTML report is generated automatically upon execution at `reports/report.html`.
To open it on Windows:

```bash
start reports/report.html

```

### Pytest Configuration (`pytest.ini`)

```ini
[pytest]
addopts = --html=reports/report.html --self-contained-html -v --tb=short
testpaths = tests

```

### Custom CLI Options

| Option | Default | Description |
| --- | --- | --- |
| `--headless` | `False` | Runs Chrome in headless mode without a UI. |
| `--base-url` | `https://sfdev.4review.info/magazine` | Override the target URL for different environments. |

---

##  Test Scope

###  In Scope

* Form UI element rendering and default states.
* Field-level JS validation (Email, PAN, Mobile, Amount).
* Boundary Value Analysis (Max length, integer overflows).
* Security validation (XSS, SQLi payload handling).
* End-to-end flow stopping exactly at the “Proceed To Pay” click.

### Out of Scope

* Payment gateway processing (Razorpay).
* Database validation / Admin portal.
* Performance and load testing.
* Post-payment email receipts.

---

## Test Coverage Breakdown (74 Tests Total)

| Category | Count |
| --- | --- |
| UI & Element State | 5 |
| E2E Happy Path (Varying Amounts/Types) | 8 |
| Dropdown Functionality | 7 |
| Mandatory Field Validation | 5 |
| Security (XSS / SQLi) | 6 |
| Negative & Boundary (PAN, Email, Mobile, Amount) | 43 |

### Defect Summary (Logged in Excel Report)

| Severity | Count |
| --- | --- |
| High | 7 |
| Medium | 3 |
| Low | 2 |

---

##  Contribution Guidelines

1. Add new UI locators strictly in `donate_page.py`.
2. Do not use `time.sleep()`; utilize inherited explicit waits from `base_page.py`.
3. Include descriptive test docstrings containing the linked TC-ID.
4. Always run `pytest --headless` to ensure CI/CD compatibility before submitting changes.

```

