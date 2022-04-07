import unittest

import jsonpickle
import selenium
import tzlocal
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from tauk.context.context import TaukContext
from tauk.context.test_case import TestCase
from tauk.context.test_data import TestData
from tauk.context.test_suite import TestSuite
from tauk.enums import TestStatus, AutomationTypes, PlatformNames, BrowserNames
from tauk.tauk_webdriver import Tauk
from tests.utils import mock


# Tauk(api_token='api_token', project_id='project_id')


class TestDataTest(unittest.TestCase):
    api_token = 'api-token'
    project_id = 'project-id'
    expected_run_id = '6d917db6-cf5d-4f30-8303-6eefc35e7558'

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()

    @mock(urls=[f'https://www.tauk.com/api/v1/execution/{project_id}/initialize',
                f'https://www.tauk.com/api/v1/execution/{project_id}/{expected_run_id}/report/upload'],
          json_responses=[{'run_id': expected_run_id, 'message': 'success'}, {'message': 'success'}],
          statuses=[200, 200])
    @Tauk.observe(custom_test_name='custom name')
    def test_success_test_case_data(self):
        options = Options()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)
        Tauk.register_driver(self.driver)
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
            self.assertDictEqual(tc['capabilities'], self.driver.capabilities, 'Appium server version is not None')

            self.assertNotIn('error', tc.keys(), 'Error is not None')
            self.assertNotIn('code_context', tc.keys(), 'Error is not None')
            self.assertNotIn('excluded', tc.keys(), 'Error is not None')
            self.assertNotIn('appium_server_version', tc.keys(), 'Error is not None')
            self.assertNotIn('tags', tc.keys(), 'Error is not None')
            self.assertNotIn('user_data', tc.keys(), 'Error is not None')
            self.assertNotIn('log', tc.keys(), 'Error is not None')

        return validate


if __name__ == '__main__':
    unittest.main()
