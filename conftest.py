import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def pytest_addoption(parser):
    parser.addoption("--headless", action="store_true", default=False,
                     help="Run tests in headless mode")
    parser.addoption("--base-url", action="store",
                     default="https://sfdev.4review.info/magazine",
                     help="Base URL for the application")


@pytest.fixture(scope="session")
def base_url(request):
    return request.config.getoption("--base-url")


@pytest.fixture(scope="function")
def driver(request):
    headless = request.config.getoption("--headless")

    chrome_options = Options()

    if headless:
        chrome_options.add_argument("--headless=new")

    
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-search-engine-choice-screen")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--no-default-browser-check")
    chrome_options.add_argument("--remote-debugging-port=0")

    
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")

    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-logging", "enable-automation"]
    )

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(0)

    yield driver

    try:
        driver.quit()
    except Exception:
        pass  


@pytest.fixture(scope="function")
def donate_page(driver, base_url):
    from pages.donate_page import DonatePage
    page = DonatePage(driver)
    page.navigate_to_donate(base_url)
    return page
