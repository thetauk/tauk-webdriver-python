import time
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support import expected_conditions
from tests.test_base import TestBase
from tests.project_capabilities import ProjectCapabilities
# Import Tauk
from tauk import Tauk


class ContactsAndroidTests(TestBase):
    app_package = "com.android.contacts"

    def pre_launch(self):
        self.caps = ProjectCapabilities.android_base_capabilities()
        self.caps["appPackage"] = self.app_package
        self.caps["appActivity"] = "com.android.contacts.activities.PeopleActivity"
        self.caps["noReset"] = True

    def setUp(self):
        super(ContactsAndroidTests, self).setUp()
        # Initialize Tauk with your api_token, project_id, and driver
        Tauk.initialize(
            api_token="",
            project_id="",
            driver=self.driver
        )

    def tearDown(self):
        time.sleep(5)
        print("Test Finished")
        self.test_end_time_ms = int(time.time() * 1000)
        # Before you quit your driver session, call Tauk.upload()
        Tauk.upload()
        self.driver.quit()

    # Decorate the test cases you want to monitor with @Tauk.observe
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
