import typing
import unittest

import jsonpickle
import selenium
import tzlocal

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from tauk.context.context import TaukContext
from tauk.context.test_case import TestCase
from tauk.context.test_data import TestData
from tauk.context.test_suite import TestSuite
from tauk.enums import TestStatus, AutomationTypes, PlatformNames, BrowserNames
from tauk.listeners.unittest_listener import TaukListener
from tauk.tauk_webdriver import Tauk
from tests.utils import mock_success


class TestDataTest(unittest.TestCase):
    expected_run_id = '6d917db6-cf5d-4f30-8303-6eefc35e7558'
    options = Options()
    driver = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.options = Options()
        cls.options.headless = True
        cls.driver = webdriver.Chrome(options=cls.options)

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, 'driver') and cls.driver:
            cls.driver.quit()

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    @mock_success()
    def test_1_success_test_case_data(self):
        Tauk.register_driver(TestDataTest.driver)
        self.driver.get('https://www.tauk.com')

        def validate(file_name, method_name, ctx: TaukContext, test_data: TestData, test_suite: TestSuite,
                     test_case: TestCase):
            json_data = jsonpickle.decode(ctx.get_json_test_data(file_name, method_name))
            tc = json_data['test_suites'][0]['test_cases'][0]
            self.assertEqual(tc['custom_name'], 'custom name', 'Invalid custom name')
            self.assertEqual(tc['method_name'], 'test_success_test_case_data', 'Invalid method name')
            self.assertEqual(tc['status'], TestStatus.PASSED.value, 'Invalid test status')
            self.assertEqual(tc['automation_type'], AutomationTypes.SELENIUM.value, f'Invalid automation type')
            self.assertEqual(tc['platform_name'], PlatformNames.MACOS.value, 'Invalid platform name')
            self.assertEqual(tc['browser_name'], BrowserNames.CHROME.value, 'Invalid browser name')
            self.assertTrue(len(tc['browser_version']) > 0, f'Invalid browser version {tc["browser_version"]}')
            self.assertEqual(len(str(tc['start_timestamp'])), 13, f'Invalid start timestamp {tc["start_timestamp"]}')
            self.assertEqual(len(str(tc['end_timestamp'])), 13, f'Invalid end timestamp {tc["end_timestamp"]}')
            self.assertTrue(tc['end_timestamp'] > tc['start_timestamp'],
                            f'Invalid start[{tc["start_timestamp"]}] and end timestamp[{tc["end_timestamp"]}]')
            self.assertEqual(tc['timezone'], tzlocal.get_localzone_name(), 'Invalid timezone')
            self.assertTrue(len(tc['screenshot']) > 100, 'Invalid screenshot')
            self.assertTrue(len(tc['view']) > 100, 'Invalid view')
            self.assertEqual(tc['webdriver_client_version'], selenium.__version__, 'Invalid webdriver client version')
            self.assertEqual(tc['browser_driver_version'], self.driver.capabilities['chrome']['chromedriverVersion'],
                             'Invalid chrome driver version')
            self.assertDictEqual(tc['capabilities'], self.driver.capabilities, 'capabilities does not match')

            self.assertNotIn('error', tc.keys(), 'error is not None')
            self.assertNotIn('code_context', tc.keys(), 'code_context is not None')
            self.assertNotIn('excluded', tc.keys(), 'excluded is not None')
            self.assertNotIn('appium_server_version', tc.keys(), 'appium_server_version is not None')
            self.assertNotIn('tags', tc.keys(), 'tags is not None')
            self.assertNotIn('user_data', tc.keys(), 'user_data is not None')
            self.assertNotIn('log', tc.keys(), 'log is not None')

        return validate

    def validate_failure(file_name, method_name, ctx: TaukContext, test_data: TestData, test_suite: TestSuite,
                         test_case: TestCase):
        json_data = jsonpickle.decode(ctx.get_json_test_data(file_name, method_name))
        tc = json_data['test_suites'][0]['test_cases'][0]
        t = unittest.TestCase()
        t.assertEqual(tc['method_name'], 'test_2_failure_test_case_data', 'Invalid method name')
        t.assertEqual(tc['status'], TestStatus.FAILED.value, 'Invalid test status')
        t.assertEqual(tc['aucatomation_type'], AutomationTypes.SELENIUM.value, f'Invalid automation type')
        t.assertEqual(tc['platform_name'], PlatformNames.MACOS.value, 'Invalid platform name')
        t.assertEqual(tc['browser_name'], BrowserNames.CHROME.value, 'Invalid browser name')
        t.assertTrue(len(tc['browser_version']) > 0, f'Invalid browser version {tc["browser_version"]}')
        t.assertEqual(len(str(tc['start_timestamp'])), 13, f'Invalid start timestamp {tc["start_timestamp"]}')
        t.assertEqual(len(str(tc['end_timestamp'])), 13, f'Invalid end timestamp {tc["end_timestamp"]}')
        t.assertTrue(tc['end_timestamp'] > tc['start_timestamp'],
                     f'Invalid start[{tc["start_timestamp"]}] and end timestamp[{tc["end_timestamp"]}]')
        t.assertEqual(tc['timezone'], tzlocal.get_localzone_name(), 'Invalid timezone')
        t.assertTrue(len(tc['screenshot']) > 100, 'Invalid screenshot')
        t.assertTrue(len(tc['view']) > 100, 'Invalid view')
        t.assertEqual(tc['webdriver_client_version'], selenium.__version__, 'Invalid webdriver client version')
        t.assertEqual(tc['browser_driver_version'], TestDataTest.driver.capabilities['chrome']['chromedriverVersion'],
                      'Invalid chrome driver version')
        t.assertDictEqual(tc['capabilities'], TestDataTest.driver.capabilities, 'Capabilitites does not match')
        t.assertIsInstance(tc['code_context'], typing.List, 'code_context must be of list type')
        t.assertTrue(len(tc['code_context']) > 0, 'code_context should not be a empty list')
        t.assertCountEqual(tc['error'].keys(),
                           ['error_type', 'error_msg', 'line_number', 'invoked_func', 'code_executed'])
        t.assertEqual(tc['error']['error_type'], 'NoSuchElementException')
        t.assertTrue(len(tc['error']['error_msg']) > 0)
        t.assertTrue(tc['error']['line_number'] > 0)
        t.assertEqual(tc['error']['invoked_func'], 'test_2_failure_test_case_data')
        t.assertTrue(len(tc['error']['code_executed']) > 0)

        t.assertNotIn('custom_name', tc.keys(), 'custom_name is not None')
        t.assertNotIn('excluded', tc.keys(), 'excluded is not None')
        t.assertNotIn('appium_server_version', tc.keys(), 'appium_server_version is not None')
        t.assertNotIn('tags', tc.keys(), 'tags is not None')
        t.assertNotIn('user_data', tc.keys(), 'user_data is not None')
        t.assertNotIn('log', tc.keys(), 'log is not None')

    @unittest.expectedFailure
    @mock_success(validation=validate_failure)
    def test_2_failure_test_case_data(self):
        Tauk.register_driver(self.driver)
        self.driver.get('https://www.tauk.com')
        self.driver.find_element(By.ID, 'unknown-id')


if __name__ == '__main__':
    Tauk(api_token="api-token", project_id="project-id")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestDataTest)
    unittest.TextTestRunner(resultclass=TaukListener).run(suite)
