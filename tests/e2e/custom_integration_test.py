from selenium import webdriver

from tauk.tauk_webdriver import Tauk
from tests.e2e.custom_integration_support import CustomIntegrationSupport


class CustomIntegrationTest:
    @Tauk.observe(test_name="test something", excluded=True)
    def test_something(self):
        self.driver = webdriver.Chrome()
        Tauk.register_driver(self.driver)
        # CustomIntegrationSupport().another_register_driver(self.driver)
        print('Custom integration test')
        self.driver.get('https://www.tauk.com')
        # assert False, 'Failed with assert'
        # self.driver.quit()


if __name__ == '__main__':
    # tauk = Tauk(api_token='dsdfs', project_id='')
    t = CustomIntegrationTest()
    t.test_something()
    t.driver.quit()

    # my_function(2, 7)
