import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions

from tests.chrome.project_capabilities import ProjectCapabilities
from tests.chrome.test_base import TestBase
# Import Tauk
from tauk import Tauk


class ChromeTests(TestBase):

    def pre_launch(self):
        self.caps = ProjectCapabilities.base_capabilities()

    def setUp(self):
        super().setUp()
        Tauk.initialize(api_token="5WOnv-KtB2MoV5RlOiK3ONrDCnw",
                        project_id="sAm5sRaiQ", driver=self.driver)

    def tearDown(self):
        time.sleep(5)
        print("Test Finished")
        self.test_end_time_ms = int(time.time() * 1000)
        # Tauk.upload(
        #     custom_session_upload_url="http://127.0.0.1:5000/api/v1/session/upload")
        self.driver.quit()

    @Tauk.observe
    def test_AppiumIO_GettingStarted(self):
        self.driver.get("https://appium.io/")

        time.sleep(1)
        print("Clicking on the [Nav Bar] Button")
        self.wait.until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//button[@data-target="#bs-example-navbar-collapse-1"]'))
        ).click()

        time.sleep(1)
        print("Clicking on the [Getting Started] Button")
        self.wait.until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@data-localize="getting-started-nav-link"]'))
        ).click()

        time.sleep(1)
        print("Clicking on the [Installing Appium] Button")
        self.wait.until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//a[text()="Installing Appium"]'))
        ).click()

        time.sleep(1)
        print("Clicking on the [Driver-Specific Setup] Button")
        self.wait.until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//a[text()="Driver-Specific Setup"]'))
        ).click()

        time.sleep(1)
        print("Clicking on the [Verifying the Installation] Button")
        self.wait.until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//a[text()="Verifying the Installation"]'))
        ).click()

        time.sleep(1)
        print("Clicking on the [Appium Clients] Button")
        self.wait.until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//a[text()="Appium Clients"]'))
        ).click()

        time.sleep(1)
        print("Clicking on the [Starting Appium] Button")
        self.wait.until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//a[text()="Starting Appium"]'))
        ).click()

        time.sleep(1)
        print("Clicking on the [Running Your First Test] Button")
        self.wait.until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//a[text()="Running Your First Test"]'))
        ).click()

        time.sleep(1)
        print("Clicking on the [What's Next] Button")
        self.wait.until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//a[text()="What\'s Next"]'))
        ).click()

        time.sleep(5)
