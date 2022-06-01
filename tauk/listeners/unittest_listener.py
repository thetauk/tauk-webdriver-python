import inspect
import logging
import os
import traceback
import unittest

from datetime import datetime, timezone
from typing import Dict
from tauk.config import TaukConfig
from tauk.context.test_case import TestCase
from tauk.enums import TestStatus, AutomationTypes
from tauk.tauk_webdriver import Tauk
from tauk.utils import attach_companion_artifacts, upload_attachments

logger = logging.getLogger('tauk')


def _should_observe(test: unittest.case.TestCase):
    return hasattr(test, 'tauk_skip') and test.tauk_skip is True


class TaukListener(unittest.TestResult):
    def __init__(self, stream, descriptions, verbosity):
        self.tests: Dict[str, TestCase] = {}
        self.test_filename = None
        super().__init__(stream, descriptions, verbosity)

    def startTestRun(self) -> None:
        logger.info("# Test Run Started ---")
        self.tests: Dict[str, TestCase] = {}

        # Check if Tauk is initialized because any class subclassing this listener
        # should have the ability to customize Tauk Config
        if not Tauk.is_initialized():
            Tauk(TaukConfig())

        super().startTestRun()

    def stopTestRun(self) -> None:
        logger.info('# Test Run Stopped ---')
        super().stopTestRun()

    def startTest(self, test: unittest.case.TestCase) -> None:
        if _should_observe(test):
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
        if _should_observe(test):
            logger.debug(f'stopTest: Skipping Tauk observe for the test [{test.id()}] ---')
            return

        logger.info(f'# Test Stopped [{test.id()}] ---')
        try:
            test_case = self.tests[test.id()]
            test_case.end_timestamp = int(datetime.now(tz=timezone.utc).timestamp() * 1000)

            if test_case.automation_type is AutomationTypes.APPIUM:  # Capture Appium logs
                try:
                    test_case.capture_appium_logs()
                except Exception as ex:
                    logger.error('Failed to capture appium server logs', exc_info=ex)

            ctx = Tauk.get_context()
            caller_filename = inspect.getfile(test.__class__)
            caller_rel_filename = os.path.relpath(caller_filename, os.getcwd())
            upload_result = ctx.api.upload(ctx.get_json_test_data(caller_rel_filename, test_case.method_name))
            test_case.id = upload_result.get(caller_rel_filename).get(test_case.method_name)

            # Attach companion artifacts
            attach_companion_artifacts(ctx.companion, test_case)
            # Upload attachments
            upload_attachments(ctx.api, test_case)
        except Exception as ex:
            logger.error(f'Failed to update test results for the test {test.id()}', exc_info=ex)

    def addError(self, test: unittest.case.TestCase, err: tuple) -> None:
        super().addError(test, err)
        if _should_observe(test):
            logger.debug(f'addError: Skipping Tauk observe for the test [{test.id()}] ---')
            return

        logger.info(f'# Test Errored [{test.id()}] ---')
        test_case = self.tests[test.id()]
        traceback.print_exception(*err)
        test_func = getattr(test, test_case.method_name)
        test_case.capture_failure_data(self.test_filename, err, test_func)

    def addFailure(self, test: unittest.case.TestCase, err: tuple) -> None:
        super().addFailure(test, err)
        if _should_observe(test):
            logger.debug(f'addFailure: Skipping Tauk observe for the test [{test.id()}] ---')
            return

        logger.info(f'# Test Failed [{test.id()}] ---')
        test_case = self.tests[test.id()]
        traceback.print_exception(*err)
        test_func = getattr(test, test_case.method_name)
        test_case.capture_failure_data(self.test_filename, err, test_func)

    def addSuccess(self, test: unittest.case.TestCase) -> None:
        super().addSuccess(test)
        if _should_observe(test):
            logger.debug(f'addSuccess: Skipping Tauk observe for the test [{test.id()}] ---')
            return

        logger.info(f'# Test Passed [{test.id()}] ---')
        self.tests[test.id()].capture_success_data()

    def addSkip(self, test: unittest.case.TestCase, reason: str) -> None:
        super().addSkip(test, reason)
        if _should_observe(test):
            logger.debug(f'addSkip: Skipping Tauk observe for the test [{test.id()}] ---')
            return

        logger.info(f'# Test Skipped [{test.id()}] ---')
        self.tests[test.id()].excluded = True
