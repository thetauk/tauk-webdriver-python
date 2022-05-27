import unittest

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from tauk.tauk_webdriver import Tauk
from tests.utils import mock_success


class UnitTestListenerTestOne(unittest.TestCase):

    def tearDown(self) -> None:
        self.driver.quit()
        pass

    @mock_success(multiprocess=True)
    def test_one(self):
        print('running test one')
        options = Options()
        options.headless = True

        self.driver = webdriver.Chrome(options=options)
        Tauk.register_driver(self.driver)
        self.driver.get('https://www.tauk.com')
        # self.driver.find_element(By.ID, 'nonexisting')
