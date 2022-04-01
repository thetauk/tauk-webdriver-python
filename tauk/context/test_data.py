import logging
import time
import typing
from datetime import datetime

import jsonpickle
import tzlocal

import tauk
from tauk.context.test_case import TestCase
from tauk.context.test_suite import TestSuite
from tauk.exceptions import TaukException
from tauk.utils import get_filtered_object

logger = logging.getLogger('tauk')


class TestData:
    def __init__(self) -> None:
        self.tauk_client_version = tauk.__version__
        self.language = 'python'
        self.start_timestamp = int(datetime.utcnow().timestamp() * 1000)
        self.timezone = tzlocal.get_localzone_name()
        self.dst = (time.localtime().tm_isdst != 0)
        self._test_suites: typing.List[TestSuite] = []
        self.dummy: str | None = None

    def __getstate__(self):
        state = get_filtered_object(self, include_private=True)
        # state['test_suites'] = self.test_suites
        return state

    @property
    def test_suites(self):
        return self._test_suites

    def get_test_suite(self, filename) -> TestSuite | None:
        for suite in self._test_suites:
            if suite.filename == filename:
                return suite
        return None

    def add_test_case(self, filename: str, testcase: TestCase):
        # Ex: '/Users/aj/tauk/tauk-webdriver-python/tests/e2e/custom_integration_test.py'
        suite = self.get_test_suite(filename)
        if suite is None:
            suite = TestSuite(filename)
            self._test_suites.append(suite)

        suite.add_testcase(testcase)

    # def get_json_test_data(self, test_suite_filename, test_method_name):
    #     suite = self.get_test_suite(test_suite_filename)
    #     if not suite:
    #         raise TaukException(f'Could not find suite with filename {test_suite_filename}')
    #
    #     suite_copy = copy.deepcopy(suite)
    #     # Clean up tests
    #     for test in suite_copy.test_cases:
    #         if test.method_name != test_method_name:
    #             suite_copy.test_cases.remove(test)
    #
    #     json_data = {
    #         "test_suites": [
    #             suite_copy
    #         ]
    #     }
    #
    #     return jsonpickle.encode(json_data, unpicklable=False, indent=3)
