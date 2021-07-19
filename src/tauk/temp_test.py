import sys
import time
import unittest
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from appium.webdriver import Remote
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support import expected_conditions
from tauk.tauk_appium import Tauk


class ProjectCapabilities:

    @staticmethod
    def android_base_capabilities() -> dict:
        android_caps = {"newCommandTimeout": 1800,
                        "deviceName": "Android Emulator",
                        "platformName": "Android",
                        "automationName": "UiAutomator2",
                        "appPackage": "com.android.settings",
                        "appActivity": ".Settings",
                        "autoAcceptAlerts": True}
        return android_caps

    @staticmethod
    def ios_base_caps() -> dict:
        ios_caps = {"newCommandTimeout": 1800,
                    "deviceName": "iPhone 12 Pro Max",
                    "automationName": "XCUITest",
                    "platformVersion": "14.3",
                    "platformName": "iOS",
                    "bundleId": "com.apple.Preferences"}
        return ios_caps


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
        self.driver = Remote(self.webdriver_url, self.caps)
        self.session_id = self.driver.session_id
        self.wait = WebDriverWait(self.driver, 20)
        self.wait_zero_seconds = WebDriverWait(self.driver, 0)
        self.test_start_time_ms = int(time.time() * 1000)

    def tearDown(self):
        time.sleep(5)
        print("Test Finished")
        self.test_end_time_ms = int(time.time() * 1000)
        self.driver.quit()


class ContactsAndroidTests(TestBase):
    app_package = "com.android.contacts"

    def pre_launch(self):
        self.caps = ProjectCapabilities.android_base_capabilities()
        self.caps["appPackage"] = self.app_package
        self.caps["appActivity"] = "com.android.contacts.activities.PeopleActivity"
        self.caps["noReset"] = True

    def setUp(self):
        super(ContactsAndroidTests, self).setUp()
        Tauk.initialize(
            api_token="",
            project_id="",
            driver=self.driver,
        )

    def tearDown(self):
        time.sleep(5)
        print("Test Finished")
        self.test_end_time_ms = int(time.time() * 1000)
        Tauk.upload(
            custom_session_upload_url="http://127.0.0.1:5000/api/v1/session/upload")
        self.driver.quit()

    @Tauk.observe
    def test_Contacts_AddNewContact(self):
        print("Clicking on the [Add] Button")
        self.wait.until(expected_conditions.presence_of_element_located(
            (MobileBy.ID, "com.android.contacts:id/floating_action_button"))
        ).click()

        first_name: str = "Tauk"
        print("Sending Keys to the First name field [{}]".format(first_name))
        self.wait.until(expected_conditions.presence_of_element_located(
            (MobileBy.ANDROID_UIAUTOMATOR, "new UiSelector().text(\"First name\")"))
        ).send_keys(first_name)

        last_name: str = "Samples"
        print("Sending Keys to the Last name field [{}]".format(last_name))
        self.wait.until(expected_conditions.presence_of_element_located(
            (MobileBy.ANDROID_UIAUTOMATOR, "new UiSelector().text(\"Last name\")"))
        ).send_keys(last_name)

        print("Clicking on the [Save] Button")
        self.wait.until(expected_conditions.presence_of_element_located(
            (MobileBy.ID, "com.android.contacts:id/editor_menu_save_button"))
        ).click()

        print("Clicking on the [More options] Button")
        self.wait.until(expected_conditions.presence_of_element_located(
            (MobileBy.ANDROID_UIAUTOMATOR, "new UiSelector().description(\"More options\")"))
        ).click()

        print("Clicking on the [Delete] Button")
        self.wait.until(expected_conditions.presence_of_element_located(
            (MobileBy.ANDROID_UIAUTOMATOR, "new UiSelector().text(\"Delete\")"))
        ).click()

        # to avoid StaleElementException
        time.sleep(2)

        print("Clicking on the [Delete] Button")
        self.wait.until(expected_conditions.presence_of_element_located(
            (MobileBy.ANDROID_UIAUTOMATOR, "new UiSelector().text(\"DELETE\")"))
        ).click()

        assert True == False

    def test_Contacts_Failure(self):
        print("Clicking on the [Add] Button")
        self.wait.until(expected_conditions.presence_of_element_located(
            (MobileBy.ID, "com.android.contacts:id/floating_action_button"))
        ).click()

        first_name: str = "Tauk"
        print("Sending Keys to the First name field [{}]".format(first_name))
        self.wait.until(expected_conditions.presence_of_element_located(
            (MobileBy.ANDROID_UIAUTOMATOR, "new UiSelector().text(\"First name\")"))
        ).send_keys(first_name)

        last_name: str = "Samples"
        print("Sending Keys to the Last name field [{}]".format(last_name))
        self.wait.until(expected_conditions.presence_of_element_located(
            (MobileBy.ANDROID_UIAUTOMATOR, "new UiSelector().text(\"LastXX name\")"))
        ).send_keys(last_name)

    def test_Contacts_UsesVariousSelectors(self):
        self.wait.until(expected_conditions.presence_of_element_located(
            (MobileBy.XPATH, '//android.widget.ImageButton[@content-desc="Open navigation drawer"]'))
        ).click()

        self.wait.until(expected_conditions.presence_of_element_located(
            (MobileBy.ID, "com.android.contacts:id/nav_settings"))
        ).click()

        self.wait.until(expected_conditions.presence_of_element_located(
            (MobileBy.ANDROID_UIAUTOMATOR, "new UiSelector().text(\"Sort by\")"))
        ).click()

        self.wait.until(expected_conditions.presence_of_element_located(
            (MobileBy.CLASS_NAME, "android.widget.CheckedTextView"))
        ).click()

        self.wait.until(expected_conditions.presence_of_element_located(
            (MobileBy.ACCESSIBILITY_ID, "Navigate up"))
        ).click()
