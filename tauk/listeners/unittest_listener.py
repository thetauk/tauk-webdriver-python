import logging
import sys
import unittest

from tauk.tauk_webdriver import Tauk

logger = logging.getLogger('tauk')


class TaukListener(unittest.TestResult):
    def startTest(self, test: unittest.case.TestCase) -> None:
        logger.info("### startTest")
        super().startTest(test)
        self.tauk = Tauk.get_instance()

    def stopTest(self, test: unittest.case.TestCase) -> None:
        super().stopTest(test)
        logger.info("### stopTest")

    def startTestRun(self) -> None:
        super().startTestRun()
        logger.info("### startTestRun")

    def stopTestRun(self) -> None:
        super().stopTestRun()
        sys.exc_info()
        logger.info("### stopTestRun")

    def addError(self, test: unittest.case.TestCase, err: tuple) -> None:
        super().addError(test, err)
        logger.info("### addError")

    def addFailure(self, test: unittest.case.TestCase, err: tuple) -> None:
        super().addFailure(test, err)
        logger.info("### addFailure")

    def addSuccess(self, test: unittest.case.TestCase) -> None:
        super().addSuccess(test)
        logger.info("### addSuccess")

    def addSkip(self, test: unittest.case.TestCase, reason: str) -> None:
        super().addSkip(test, reason)
        logger.info("### addSkip")

    def addExpectedFailure(self, test: unittest.case.TestCase, err: tuple) -> None:
        super().addExpectedFailure(test, err)
        logger.info("### addExpectedFailure")

    def addUnexpectedSuccess(self, test: unittest.case.TestCase) -> None:
        super().addUnexpectedSuccess(test)
        logger.info("### addUnexpectedSuccess")

    def addSubTest(self, test: unittest.case.TestCase, subtest: unittest.case.TestCase,
                   err: tuple | None) -> None:
        super().addSubTest(test, subtest, err)
        logger.info("### addSubTest")
