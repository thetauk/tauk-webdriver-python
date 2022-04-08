import logging
import time
import typing
from datetime import datetime, timezone

import tzlocal

import tauk
from tauk.context.test_case import TestCase
from tauk.context.test_suite import TestSuite
from tauk.utils import get_filtered_object

logger = logging.getLogger('tauk')


class TestData:
    def __init__(self) -> None:
        self.tauk_client_version = tauk.__version__
        self.language = 'python'
        self.start_timestamp = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
        self.timezone = tzlocal.get_localzone_name()
        self.dst = (time.localtime().tm_isdst != 0)
        self._test_suites: typing.List[TestSuite] = []

    def __getstate__(self):
        state = get_filtered_object(self, include_private=True)
        # state['test_suites'] = self.test_suites
        return state

    @property
    def test_suites(self):
        return self._test_suites

    def get_test_suite(self, filename) -> TestSuite:
        for suite in self._test_suites:
            if suite.filename == filename:
                return suite
        return None

    def add_test_case(self, filename: str, test_case: TestCase):
        suite = self.get_test_suite(filename)
        if suite is None:
            suite = TestSuite(filename)
            self._test_suites.append(suite)

        suite.add_testcase(test_case)
