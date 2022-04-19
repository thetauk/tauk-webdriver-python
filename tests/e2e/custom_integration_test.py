import logging

from appium.webdriver.common.mobileby import MobileBy
from selenium import webdriver as selenium_driver
from appium import webdriver as appium_driver
from tauk.tauk_webdriver import Tauk

logger = logging.getLogger('tauk')


class CustomIntegrationTest:
    @Tauk.observe(custom_test_name="Test Selenium")
    def test_selenium(self):
        self.driver = selenium_driver.Chrome()
        # self.driver = selenium_driver.Edge()
        Tauk.register_driver(self.driver)
        # CustomIntegrationSupport().another_register_driver(self.driver)
        print('Custom integration test')
        self.driver.get('https://www.tauk.com')
        # assert False, 'Failed with assert'
        # self.driver.quit()

    @Tauk.observe()
    def test_appium(self):
        logger.info('Starting test')
        caps = {
            "deviceName": "Pixel 5",
            "udid": "emulator-5554",
            "platformName": "Android",
            # "browserName": "chrome",
            "appPackage": "io.aj.sample",
            "appActivity": ".MainActivity",
            "automationName": "UiAutomator2",
            "newCommandTimeout": 0
        }
        self.driver = appium_driver.Remote("http://localhost:4723/wd/hub", caps)
        Tauk.register_driver(driver=self.driver)
        self.driver.implicitly_wait(30)
        self.driver.find_element(MobileBy.ID, 'stocksButton').click()
        logger.info('Test complete')


if __name__ == '__main__':
    # Tauk(api_token='test', project_id='test')
    t = CustomIntegrationTest()
    # t.test_selenium()
    t.test_appium()
    t.driver.quit()

    # my_function(2, 7)
