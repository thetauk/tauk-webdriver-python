import inspect
import logging
import os
import traceback
import unittest
from datetime import datetime, timezone
from typing import Dict

from tauk.context.test_case import TestCase
from tauk.enums import TestStatus
from tauk.tauk_webdriver import Tauk

logger = logging.getLogger('tauk')


class TaukListener(unittest.TestResult):
    multiprocess_run = False

    def __init__(self, stream, descriptions, verbosity):
        self.tests = None
        self.test_filename = None
        super().__init__(stream, descriptions, verbosity)

    def startTestRun(self) -> None:
        logger.info("# Test Run Started ---")
        self.tests: Dict[str, TestCase] = {}
        Tauk(multi_process_run=self.multiprocess_run) if not Tauk.is_initialized() else None
        super().startTestRun()

    def stopTestRun(self) -> None:
        logger.info('# Test Run Stopped ---')
        super().stopTestRun()

    def startTest(self, test: unittest.case.TestCase) -> None:
        logger.info(f'# Test Started [{test.id()}] ---')
        self.tests[test.id()] = TestCase()
        self.tests[test.id()].start_timestamp = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
        self.tests[test.id()].custom_name = test.shortDescription()

        caller_filename = inspect.getfile(test.__class__)
        self.test_filename = caller_filename.replace(f'{os.getcwd()}{os.sep}', '')

        test_case_name = test.id().split('.')[-1]
        self.tests[test.id()].method_name = test_case_name

        Tauk.get_context().test_data.add_test_case(self.test_filename, self.tests[test.id()])

        super().startTest(test)

    def stopTest(self, test: unittest.case.TestCase) -> None:
        logger.info(f'# Test Stopped [{test.id()}] ---')
        super().stopTest(test)

        self.tests[test.id()].end_timestamp = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
        self.tests[test.id()].capture_appium_logs()
        ctx = Tauk.get_context()

        caller_filename = inspect.getfile(test.__class__)
        caller_relative_filename = caller_filename.replace(f'{os.getcwd()}{os.sep}', '')
        ctx.api.upload(ctx.get_json_test_data(caller_relative_filename, self.tests[test.id()].method_name))

    def addError(self, test: unittest.case.TestCase, err: tuple) -> None:
        logger.info(f'# Test Errored [{test.id()}] ---')
        super().addError(test, err)
        self.tests[test.id()].status = TestStatus.FAILED

        exctype, value, tb = err
        traceback.print_exception(exctype, value, tb)
        self.tests[test.id()].capture_error(self.test_filename, err)

    def addFailure(self, test: unittest.case.TestCase, err: tuple) -> None:
        logger.info(f'# Test Failed [{test.id()}] ---')
        super().addFailure(test, err)
        self.tests[test.id()].status = TestStatus.FAILED

        exctype, value, tb = err
        traceback.print_exception(exctype, value, tb)
        self.tests[test.id()].capture_error(self.test_filename, err)

    def addSuccess(self, test: unittest.case.TestCase) -> None:
        logger.info(f'# Test Passed [{test.id()}] ---')
        super().addSuccess(test)
        self.tests[test.id()].status = TestStatus.PASSED

    def addSkip(self, test: unittest.case.TestCase, reason: str) -> None:
        logger.info(f'# Test Skipped [{test.id()}] ---')
        super().addSkip(test, reason)
        self.tests[test.id()].excluded = True
