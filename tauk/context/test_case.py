import logging
import re
from contextlib import suppress

import tzlocal
import inspect

import traceback
import typing

from tauk.context.test_error import TestError
from tauk.enums import AutomationTypes, PlatformNames, TestStatus, BrowserNames
from tauk.exceptions import TaukException
from tauk.utils import get_filtered_object, get_appium_server_version, get_browser_driver_version

logger = logging.getLogger('tauk')


class TestCase:

    def __init__(self) -> None:
        self._id: str = None
        self._custom_name: str = None
        self._method_name: str = None
        self._status: TestStatus = None
        self.excluded: bool = False
        self._automation_type: AutomationTypes = None
        self._platform_name: PlatformNames = None
        self.platform_version: str = None
        self.browser_name: str = None
        self.browser_version: str = None
        self._start_timestamp: int = None
        self._end_timestamp: int = None
        self.timezone: str = None  # "America/Los_Angeles"
        self._error: TestError = None
        self.screenshot: str = None
        self.view: str = None
        self._code_context: typing.List[object] = None
        self.webdriver_client_version: str = None
        self.browser_driver_version: str = None
        self.appium_server_version: str = None
        self._capabilities: {} = None
        self._tags: {} = None
        self._user_data: {} = None
        self.log: typing.List[object] = None

        self._driver_instance = None

    def __getstate__(self):
        state = get_filtered_object(self, include_private=True,
                                    filter_keys=[
                                        '_driver_instance',
                                        'excluded'
                                    ])
        if self.excluded is True:
            self.status = TestStatus.EXCLUDED
        return state

    def __deepcopy__(self, memodict={}):
        return self

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def custom_name(self):
        return self._custom_name

    @custom_name.setter
    def custom_name(self, custom_name):
        self._custom_name = custom_name

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
    def start_timestamp(self):
        return self._start_timestamp

    @start_timestamp.setter
    def start_timestamp(self, start_timestamp):
        self.timezone = tzlocal.get_localzone_name()
        self._start_timestamp = start_timestamp

    @property
    def end_timestamp(self):
        return self._end_timestamp

    @end_timestamp.setter
    def end_timestamp(self, end_timestamp):
        self._end_timestamp = end_timestamp

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
        logger.debug(f'Adding tag {tag_name}={value}')
        self._tags[tag_name] = value

    @property
    def user_data(self):
        return self._user_data

    def add_user_data(self, name, value):
        if len(name) > 100 and len(value) > 1000:
            raise TaukException('user data is too large')
        self._user_data[name] = value

    @property
    def driver_instance(self):
        return self._driver_instance

    @driver_instance.setter
    def driver_instance(self, driver_instance):
        self._driver_instance = driver_instance

    def register_driver(self, driver, test_filename=None, test_method_name=None):
        if not driver or 'webdriver' not in f'{type(driver)}':
            raise TaukException(f'Driver {type(driver)} is not of type webdriver')

        if test_filename:
            driver.tauk_test_filename = test_filename
        if test_method_name:
            driver.tauk_test_method_name = test_method_name

        def tauk_callback(func):
            def inner():
                self.capture_screenshot()
                self.capture_view_hierarchy()
                func()

            return inner

        driver.quit = tauk_callback(driver.quit)

        self.driver_instance = driver
        self.capabilities = driver.capabilities

        # Collect other data about driver
        if 'selenium' in f'{type(driver)}':
            self.automation_type = AutomationTypes.SELENIUM
            with suppress(Exception):
                import selenium as s
                self.webdriver_client_version = s.__version__
        elif 'appium' in f'{type(driver)}':
            self.automation_type = AutomationTypes.APPIUM
            with suppress(Exception):
                from appium.common.helper import library_version
                self.webdriver_client_version = library_version()
                self.appium_server_version = get_appium_server_version(driver)

        if self.automation_type is AutomationTypes.APPIUM:
            self.platform_name = PlatformNames.resolve(self.capabilities.get('platform', ''))
        else:
            self.platform_name = PlatformNames.resolve(self.capabilities.get('platformName', ''))

        self.platform_version = self.capabilities.get('platformVersion', None)
        self.browser_name = BrowserNames.resolve(self.capabilities.get('browserName', ''))
        self.browser_version = self.capabilities.get('browserVersion', None)

        self.browser_driver_version = get_browser_driver_version(driver)

    def capture_screenshot(self):
        if self.screenshot and len(self.screenshot) > 0:
            logger.debug('Screenshot is already captured')
            return
        if self.driver_instance:
            try:
                self.screenshot = self.driver_instance.get_screenshot_as_base64()
            except Exception as ex:
                logger.error("An issue occurred while trying to take a screenshot.", exc_info=ex)

    def capture_view_hierarchy(self):
        if self.view and len(self.view) > 0:
            logger.debug('View Hierarchy is already captured')
            return
        if self.driver_instance:
            try:
                if hasattr(self.driver_instance, 'contexts') and 'FLUTTER' in self.driver_instance.contexts:
                    current_context = self.driver_instance.current_context
                    self.driver_instance.switch_to.context('NATIVE_APP')
                    self.view = self.driver_instance.page_source
                    self.driver_instance.switch_to.context(current_context)
                    return

                self.view = self.driver_instance.page_source
            except Exception as ex:
                logger.error("An issue occurred while capturing view hierarchy.", exc_info=ex)

    def capture_error(self, caller_filename, exec_info):
        exc_type, exc_value, exc_traceback = exec_info
        stack_summary_list = traceback.extract_tb(exc_traceback)
        filename, line_number, invoked_func, code_executed = None, None, None, None
        for stack_trace in stack_summary_list:
            if caller_filename in stack_trace.filename:
                filename, line_number, invoked_func, code_executed = stack_trace
                break

        self.error = {
            'error_type': exc_value.__class__.__name__,
            'error_msg': str(exc_value),
            'line_number': line_number,
            'invoked_func': invoked_func,
            'code_executed': code_executed
        }
        return line_number

    def capture_success_data(self):
        self.status = TestStatus.PASSED
        self.capture_screenshot()
        self.capture_view_hierarchy()

    def capture_failure_data(self):
        self.status = TestStatus.FAILED
        self.capture_screenshot()
        self.capture_view_hierarchy()

    def capture_test_steps(self, testcase, error_line_number=0):
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

    def capture_appium_logs(self):
        def format_appium_log(log_list):
            output = []
            for event in log_list:
                # ANSI escape sequences
                # https://bit.ly/3rK88pe
                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

                # Split at first event type occurence
                # in square brackets, e.g. [HTTP]
                # https://bit.ly/3fItHEi
                split_log_msg = re.split(r'\[|\]', ansi_escape.sub(
                    '', event['message']), maxsplit=2)

                formatted_event = {
                    'timestamp': event.get('timestamp'),
                    'level': event.get('level'),
                    'type': split_log_msg[1],
                    'message': split_log_msg[2].strip()
                }

                output.append(formatted_event)
            return output

        if self.automation_type != AutomationTypes.APPIUM:
            return

        # Get last 50 log entries
        # minus the 5 log entries for issuing get_log()
        slice_range = slice(-55, -5)

        if not self.driver_instance:
            logger.warning('Not capturing appium logs because driver instance was not registered')
            return

        try:
            self.log = format_appium_log(self.driver_instance.get_log('server')[slice_range])
        except Exception as ex:
            logger.error('An issue occurred while requesting the Appium server logs.', exc_info=ex)
