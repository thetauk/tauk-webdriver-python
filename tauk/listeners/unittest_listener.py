import inspect
import logging
import os
import traceback
import unittest
from datetime import datetime, timezone
from typing import Dict

from tauk.context.test_case import TestCase
from tauk.enums import TestStatus, AutomationTypes, AttachmentTypes
from tauk.tauk_webdriver import Tauk

logger = logging.getLogger('tauk')


class TaukListener(unittest.TestResult):
    multiprocess_run = False

    def __init__(self, stream, descriptions, verbosity):
        self.tests: Dict[str, TestCase] = {}
        self.test_filename = None
        super().__init__(stream, descriptions, verbosity)

    def _should_observe(self, test):
        return hasattr(test, 'tauk_skip') and test.tauk_skip is True

    def _upload_attachments(self, testcase: TestCase):
        companion = Tauk.get_context().companion
        if companion and companion.is_running() and companion.config.is_cdp_capture_enabled():
            try:
                connected_page = companion.get_connected_page(testcase.browser_debugger_address)
                logger.debug(f'Collecting logs from the page {connected_page}')
                if connected_page:
                    try:
                        companion.close_page(testcase.browser_debugger_address)
                    except Exception:
                        pass
                    attachment_path = os.path.join(Tauk.get_context().exec_dir, 'companion', connected_page.lower())
                    companion_attachments = next(os.walk(attachment_path), (None, None, []))[2]  # only files
                    if len(companion_attachments) == 0:
                        logger.info('Did not find any companion attachments')
                    for attachment in companion_attachments:
                        testcase.add_attachment(
                            os.path.join(attachment_path, attachment),
                            AttachmentTypes.resolve_companion_log(attachment))
            except Exception as exc:
                logger.error('Failed to close browser debugger page', exc_info=exc)

        for file_path, attachment_type in testcase.attachments:
            try:
                Tauk.get_context().api.upload_attachment(file_path, attachment_type, testcase.id)
                # If it's a companion attachment we should delete it after successful upload
                if attachment_type.is_companion_attachment():
                    if os.path.exists(file_path):
                        logger.debug(f'Deleting companion attachment {file_path}')
                        os.remove(file_path)
            except Exception as ex:
                logger.error(f'Failed to upload attachment {attachment_type}: {file_path}', exc_info=ex)

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

        self.tests[test.id()] = TestCase()
        self.tests[test.id()].method_name = test_method_name
        self.tests[test.id()].start_timestamp = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
        self.tests[test.id()].custom_name = test.shortDescription()

        Tauk.get_context().test_data.add_test_case(self.test_filename, self.tests[test.id()])

        super().startTest(test)

    def stopTest(self, test: unittest.case.TestCase) -> None:
        super().stopTest(test)
        if self._should_observe(test):
            logger.debug(f'stopTest: Skipping Tauk observe for the test [{test.id()}] ---')
            return

        logger.info(f'# Test Stopped [{test.id()}] ---')
        try:
            self.tests[test.id()].end_timestamp = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
            if self.tests[test.id()].automation_type is AutomationTypes.APPIUM:
                self.tests[test.id()].capture_appium_logs()

            ctx = Tauk.get_context()

            caller_filename = inspect.getfile(test.__class__)
            caller_rel_filename = os.path.relpath(caller_filename, os.getcwd())
            upload_result = ctx.api.upload(
                ctx.get_json_test_data(caller_rel_filename, self.tests[test.id()].method_name))
            self.tests[test.id()].id = upload_result.get(caller_rel_filename).get(self.tests[test.id()].method_name)
            self._upload_attachments(self.tests[test.id()])

        except Exception as ex:
            logger.error('Failed to upload test results', exc_info=ex)

    def addError(self, test: unittest.case.TestCase, err: tuple) -> None:
        super().addError(test, err)
        if self._should_observe(test):
            logger.debug(f'addError: Skipping Tauk observe for the test [{test.id()}] ---')

            return

        logger.info(f'# Test Errored [{test.id()}] ---')
        self.tests[test.id()].status = TestStatus.FAILED

        exctype, value, tb = err
        traceback.print_exception(exctype, value, tb)
        self.tests[test.id()].capture_error(self.test_filename, err)

    def addFailure(self, test: unittest.case.TestCase, err: tuple) -> None:
        super().addFailure(test, err)
        if self._should_observe(test):
            logger.debug(f'addFailure: Skipping Tauk observe for the test [{test.id()}] ---')
            return

        logger.info(f'# Test Failed [{test.id()}] ---')
        self.tests[test.id()].status = TestStatus.FAILED

        exctype, value, tb = err
        traceback.print_exception(exctype, value, tb)
        self.tests[test.id()].capture_error(self.test_filename, err)

    def addSuccess(self, test: unittest.case.TestCase) -> None:
        super().addSuccess(test)
        if self._should_observe(test):
            logger.debug(f'addSuccess: Skipping Tauk observe for the test [{test.id()}] ---')
            return

        logger.info(f'# Test Passed [{test.id()}] ---')
        self.tests[test.id()].status = TestStatus.PASSED

    def addSkip(self, test: unittest.case.TestCase, reason: str) -> None:
        super().addSkip(test, reason)
        if self._should_observe(test):
            logger.debug(f'addSkip: Skipping Tauk observe for the test [{test.id()}] ---')
            return

        logger.info(f'# Test Skipped [{test.id()}] ---')
        self.tests[test.id()].excluded = True
