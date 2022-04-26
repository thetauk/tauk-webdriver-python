import unittest

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from tauk.tauk_webdriver import Tauk


class BaseTestCase(unittest.TestCase):
    expected_run_id = '6d917db6-cf5d-4f30-8303-6eefc35e7558'
    options = Options()
    driver = None

    def setUp(self) -> None:
        self.options = Options()
        self.options.headless = True
        self.driver = webdriver.Chrome(options=self.options)
        Tauk.register_driver(self.driver, unittestcase=self)

    def tearDown(self) -> None:
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
