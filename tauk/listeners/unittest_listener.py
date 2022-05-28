import inspect
import logging
import os
import traceback
import unittest
from datetime import datetime, timezone
from typing import Dict

from tauk.context.test_case import TestCase
from tauk.enums import TestStatus, AutomationTypes
from tauk.tauk_webdriver import Tauk

logger = logging.getLogger('tauk')


class TaukListener(unittest.TestResult):
    multiprocess_run = False

    def __init__(self, stream, descriptions, verbosity):
        self.tests = None
        self.test_filename = None
        super().__init__(stream, descriptions, verbosity)

    def _should_observe(self, test):
        return hasattr(test, 'tauk_skip') and test.tauk_skip is True

    def startTestRun(self) -> None:
        logger.info("# Test Run Started ---")
        self.tests: Dict[str, TestCase] = {}
        Tauk(multi_process_run=self.multiprocess_run) if not Tauk.is_initialized() else None
        super().startTestRun()

    def stopTestRun(self) -> None:
        logger.info('# Test Run Stopped ---')
        super().stopTestRun()

    def startTest(self, test: unittest.case.TestCase) -> None:
        if self._should_observe(test):
            logger.info(f'startTest: Skipping Tauk observe for the test [{test.id()}] ---')
            super().startTest(test)
            return

        logger.info(f'# Test Started [{test.id()}] ---')
        caller_filename = inspect.getfile(test.__class__)
        self.test_filename = caller_filename.replace(f'{os.getcwd()}{os.sep}', '')
        test_method_name = test.id().split('.')[-1]

        test_case = TestCase()
        test_case.method_name = test_method_name
        test_case.start_timestamp = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
        test_case.custom_name = test.shortDescription()

        Tauk.get_context().test_data.add_test_case(self.test_filename, test_case)
        self.tests[test.id()] = test_case

        super().startTest(test)

    def stopTest(self, test: unittest.case.TestCase) -> None:
        super().stopTest(test)
        if self._should_observe(test):
            logger.debug(f'stopTest: Skipping Tauk observe for the test [{test.id()}] ---')
            return

        logger.info(f'# Test Stopped [{test.id()}] ---')
        try:
            test_case = self.tests[test.id()]
            test_case.end_timestamp = int(datetime.now(tz=timezone.utc).timestamp() * 1000)

            if test_case.automation_type == AutomationTypes.APPIUM:
                test_case.capture_appium_logs()

            ctx = Tauk.get_context()

            caller_filename = inspect.getfile(test.__class__)
            caller_relative_filename = caller_filename.replace(f'{os.getcwd()}{os.sep}', '')
            ctx.api.upload(ctx.get_json_test_data(caller_relative_filename, self.tests[test.id()].method_name))
        except Exception as ex:
            logger.error('Failed to upload test results', exc_info=ex)

    def addError(self, test: unittest.case.TestCase, err: tuple) -> None:
        super().addError(test, err)
        if self._should_observe(test):
            logger.debug(f'addError: Skipping Tauk observe for the test [{test.id()}] ---')
            return

        logger.info(f'# Test Errored [{test.id()}] ---')
        test_case = self.tests[test.id()]
        traceback.print_exception(*err)
        test_func = getattr(test, test_case.method_name)
        test_case.capture_failure_data(self.test_filename, err, test_func)

    def addFailure(self, test: unittest.case.TestCase, err: tuple) -> None:
        super().addFailure(test, err)
        if self._should_observe(test):
            logger.debug(f'addFailure: Skipping Tauk observe for the test [{test.id()}] ---')
            return

        logger.info(f'# Test Failed [{test.id()}] ---')
        test_case = self.tests[test.id()]
        traceback.print_exception(*err)
        test_func = getattr(test, test_case.method_name)
        test_case.capture_failure_data(self.test_filename, err, test_func)

    def addSuccess(self, test: unittest.case.TestCase) -> None:
        super().addSuccess(test)
        if self._should_observe(test):
            logger.debug(f'addSuccess: Skipping Tauk observe for the test [{test.id()}] ---')
            return

        logger.info(f'# Test Passed [{test.id()}] ---')
        self.tests[test.id()].capture_success_data()

    def addSkip(self, test: unittest.case.TestCase, reason: str) -> None:
        super().addSkip(test, reason)
        if self._should_observe(test):
            logger.debug(f'addSkip: Skipping Tauk observe for the test [{test.id()}] ---')
            return

        logger.info(f'# Test Skipped [{test.id()}] ---')
        self.tests[test.id()].excluded = True
