import inspect
import json
import logging
import sys
import time
import traceback
import typing

from tauk.enums import AutomationTypes, PlatformNames, TestStatus
from tauk.exceptions import TaukException

logger = logging.getLogger('tauk')


class TestError:
    error_type: str
    error_msg: str
    line_number: int
    invoked_func: str
    code_executed: str


class TestCase:
    _id: str = None
    _name: str = None
    _method_name: str = None
    _status: TestStatus = None
    _excluded: bool = False
    _automation_type: AutomationTypes = None
    _platform_name: PlatformNames = None
    platform_version: str = None
    browser_name: str = None
    browser_version: str = None
    _start_time: float = None
    _end_time: float = None
    timezone: str = None
    _error: TestError = None
    screenshot: str = None
    view: str = None
    _code_context: typing.List[object] = None
    client_version: str = None
    driver_version: str = None
    appium_server_version: str = None
    _capabilities: {} = None
    _tags: {} = None
    _user_data: {} = None
    _driver_instance = None
    is_synced: bool = None

    def __init__(self) -> None:
        self.timezone = time.tzname[time.daylight if time.localtime().tm_isdst != 0 else 0]

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def method_name(self):
        return self._method_name

    @method_name.setter
    def method_name(self, method_name):
        self._method_name = method_name

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status: TestStatus):
        if not isinstance(status, TestStatus):
            raise TaukException(f'status [{status}] must be of type TestStatus')
        self._status = status

    @property
    def automation_type(self):
        return self._automation_type

    @automation_type.setter
    def automation_type(self, automation_type: AutomationTypes):
        self._automation_type = automation_type

    @property
    def platform_name(self):
        return self._platform_name

    @platform_name.setter
    def platform_name(self, platform_name: PlatformNames):
        self._platform_name = platform_name

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, start_time):
        self.timezone = time.tzname[time.daylight if time.localtime().tm_isdst != 0 else 0]
        self._start_time = start_time

    @property
    def end_time(self):
        return self._end_time

    @end_time.setter
    def end_time(self, end_time):
        self._end_time = end_time

    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, error):
        self._error = error

    @property
    def code_context(self):
        return self._code_context

    @code_context.setter
    def code_context(self, code_context):
        self._code_context = code_context

    @property
    def capabilities(self):
        return self._capabilities

    @capabilities.setter
    def capabilities(self, capabilities):
        self._capabilities = capabilities

    @property
    def tags(self):
        return self._tags

    def add_tag(self, tag_name, value):
        # TODO: check if tag name already exists
        self._tags[tag_name] = value

    @property
    def user_data(self):
        return self._user_data

    def add_user_data(self, name, value):
        # TODO: check if name already exists
        # Add validations like size check etc
        self._user_data[name] = value

    @property
    def driver_instance(self):
        return self._driver_instance

    @driver_instance.setter
    def driver_instance(self, driver_instance):
        self._driver_instance = driver_instance

    def register_driver(self, driver):
        self.driver_instance = driver
        # Collect other data about driver
        if 'selenium' in f'{type(driver)}':
            self.automation_type = AutomationTypes.SELENIUM
        elif 'appium' in f'{type(driver)}':
            self.automation_type = AutomationTypes.APPIUM

        self.capabilities = driver.capabilities
        self.platform_name = self.capabilities.get('platformName', '')  # TODO: handle cases where its not available
        self.platform_version = self.capabilities.get('platformVersion', '')  # TODO: handle cases where its not available
        self.browser_name = self.capabilities.get('browserName', '')
        self.browser_version = self.capabilities.get('browserVersion', '')

    def capture_screenshot(self):
        if self.driver_instance:
            try:
                self.screenshot = self.driver_instance.get_screenshot_as_base64()
            except Exception as ex:
                logger.error("An issue occurred while trying to take a screenshot.", exc_info=ex)

    def capture_view_hierarchy(self):
        if self.driver_instance:
            try:
                # TODO: Revisit flutter because if we switch context then we have to also switch back to original
                # if 'FLUTTER' in self.driver_instance.contexts:
                #     self.driver_instance.switch_to.context('NATIVE_APP')
                self.view = self.driver_instance.page_source
            except Exception as ex:
                logger.error("An issue occurred while capturing view hierarchy.", exc_info=ex)

    def capture_error(self, caller_filename, exec_info):
        exc_type, exc_value, exc_traceback = exec_info
        stack_summary_list = traceback.extract_tb(exc_traceback)
        filename, line_number, invoked_func, code_executed = None, None, None, None
        for stack_trace in stack_summary_list:
            if stack_trace.filename == caller_filename:
                filename, line_number, invoked_func, code_executed = stack_trace
                break

        self.error = (exc_value, line_number, invoked_func, code_executed)

    def capture_success_data(self):
        self.status = TestStatus.PASSED
        self.capture_screenshot()
        self.capture_view_hierarchy()

    def capture_failure_data(self):
        self.status = TestStatus.FAILED
        self.capture_screenshot()
        self.capture_view_hierarchy()

    def get_testcase_steps(self, testcase, error_line_number=0):
        testcase_source_raw = inspect.getsourcelines(testcase)
        testcase_source_clean = [step.strip() for step in testcase_source_raw[0]]
        line_number = testcase_source_raw[1]

        # Discard the initial 2 lines as they are the decorator and the testcase function name
        testcase_source_clean = testcase_source_clean[2:]
        line_number += 2

        output = []
        for step in testcase_source_clean:
            output.append(
                {
                    'line_number': line_number,
                    'line_code': step
                }
            )
            line_number += 1

        if error_line_number > 0:
            for index, value in enumerate(output):
                if value['line_number'] == error_line_number:
                    # get previous 9 lines plus the line where the error occurred
                    # ensure that the start range value is never below zero
                    # get the next 9 lines after the error occured
                    # ensure that the end range value never exceeds the len of the list
                    result = output[max(index - 9, 0): min(index + 10, len(output))]
                    self.code_context = result
        else:
            self.code_context = output


class TestSuite:
    _name: str = None
    _filename: str = None
    _class_name: str = None
    _test_cases: typing.List[TestCase] = []
    language: str = 'python'

    def __init__(self, filename) -> None:
        self._filename = filename

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, filename):
        self._filename = filename

    @property
    def class_name(self):
        return self._class_name

    @class_name.setter
    def class_name(self, class_name):
        self._class_name = class_name

    @property
    def test_cases(self):
        return self._test_cases

    def add_testcase(self, testcase: TestCase):
        self._test_cases.append(testcase)

    def get_test_case(self, test_name) -> TestCase | None:
        for test in self._test_cases:
            if test.name == test_name or test.method_name == test_name:
                return test
        return None

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def print(self):
        print(f'  name: {self.name}')
        print(f'  filename: {self.filename}')
        print(f'  class_name: {self.class_name}')
        print(f'  Test Cases:')
        for test in self.test_cases:
            print(f'    id: {test.id}')
            print(f'    name: {test.name}')
            print(f'    method_name: {test.method_name}')
            print(f'    status: {test.status}')
            print(f'    automation_type: {test.automation_type}')
            print(f'    platform_name: {test.platform_name}')
            print(f'    platform_version: {test.platform_version}')
            print(f'    browser_name: {test.browser_name}')
            print(f'    browser_version: {test.browser_version}')
            print(f'    start_time: {test.start_time}')
            print(f'    end_time: {test.end_time}')
            print(f'    timezone: {test.timezone}')
            print(f'    error: {test.error}')
            # print(f'    screenshot: {len(test.screenshot)}')
            # print(f'    view: {len(test.view)}')
            print(f'    code_context: {test.code_context}')
            print(f'    client_version: {test.client_version}')
            print(f'    driver_version: {test.driver_version}')
            print(f'    appium_server_version: {test.appium_server_version}')
            print(f'    capabilities: {test.capabilities}')
            print(f'    tags: {test.tags}')
            print(f'    user_data: {test.user_data}')
            print(f'    is_synced: {test.is_synced}')


class TestData:
    init_time: float
    _test_suites: typing.List[TestSuite] = []

    def __init__(self) -> None:
        self.init_time = time.time()

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

    def print(self):
        print(f'init_time: {self.init_time}')
        print('Test Suites:')
        for suite in self.test_suites:
            suite.print()
