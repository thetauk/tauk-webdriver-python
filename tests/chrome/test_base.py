import sys
import time
import unittest

from appium.webdriver.webdriver import WebDriver, WebDriverWait
from selenium import webdriver


class TestBase(unittest.TestCase):
    driver: WebDriver = None
    session_id: str = None
    caps: dict = None
    webdriver_url = "http://localhost:4723/wd/hub"
    test_start_time_ms: int = None
    test_end_time_ms: int = None
    wait: WebDriverWait = None
    wait_zero_seconds: WebDriverWait = None

    def pre_launch(self):
        pass

    def setUp(self):
        if not sys.warnoptions:
            import warnings
            warnings.simplefilter("ignore")
        self.pre_launch()
        self.driver = webdriver.Chrome('./bin/chromedriver')
        self.session_id = self.driver.session_id
        self.wait = WebDriverWait(self.driver, 20)
        self.wait_zero_seconds = WebDriverWait(self.driver, 0)
        self.test_start_time_ms = int(time.time() * 1000)

    def tearDown(self):
        time.sleep(5)
        print("Test Finished")
        self.test_end_time_ms = int(time.time() * 1000)
        self.driver.quit()
