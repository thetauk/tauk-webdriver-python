import logging
import os.path
import re
import tzlocal
import inspect
import traceback
import typing

from contextlib import suppress
from pathlib import Path
from tauk.companion.companion import TaukCompanion
from tauk.context.test_error import TestError
from tauk.enums import AutomationTypes, PlatformNames, TestStatus, BrowserNames, AttachmentTypes
from tauk.exceptions import TaukException
from tauk.utils import get_appium_server_version, get_browser_driver_version, get_browser_debugger_address

logger = logging.getLogger('tauk')


class TestCase(object):

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
        self._browser_debugger = {'address': '', 'page_id': ''}
        self._attachments: typing.List[tuple] = []
        self._capabilities: {} = None
        self._tags: {} = None
        self._user_data: {} = None
        self.log: typing.List[object] = None

        self._driver_instance = None

    # NOTE: Any object that should be a part of test case should be explicitly added to to_json()
    #       method
    def to_json(self):
        json = {
            'id': self.id,
            'custom_name': self.custom_name,
            'method_name': self.method_name,
            'status': TestStatus.EXCLUDED if self.excluded else self.status,
            'automation_type': self.automation_type,
            'platform_name': self.platform_name,
            'platform_version': self.platform_version,
            'browser_name': self.browser_name,
            'browser_version': self.browser_version,
            'start_timestamp': self.start_timestamp,
            'end_timestamp': self.end_timestamp,
            'timezone': self.timezone,
            'error': self.error,
            'screenshot': self.screenshot,
            'view': self.view,
            'code_context': self.code_context,
            'webdriver_client_version': self.webdriver_client_version,
            'browser_driver_version': self.browser_driver_version,
            'appium_server_version': self.appium_server_version,
            'capabilities': self.capabilities,
            'tags': self.tags,
            'user_data': self.user_data,
            'log': self.log,
        }

        return {k: v for k, v in json.items() if v}

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, external_test_id):
        self._id = external_test_id

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

    @property
    def browser_debugger_address(self):
        return self._browser_debugger.get('address')

    @property
    def browser_debugger_page_id(self):
        return self._browser_debugger.get('page_id')

    @property
    def attachments(self):
        return self._attachments

    def _connect_to_browser_debugger(self, companion: TaukCompanion):
        try:
            # TODO: Investigate possibility of using on appium
            companion.register_browser(self.browser_debugger_address)
            self._browser_debugger['page_id'] = companion.connect_page(self.browser_debugger_address)
        except Exception as ex:
            logger.error('Failed to connect to browser debugger', exc_info=ex)

    def register_driver(self, driver, companion: TaukCompanion = None, test_filename=None, test_method_name=None):
        if not driver or 'webdriver' not in f'{type(driver)}':
            raise TaukException(f'Driver {type(driver)} is not of type webdriver')

        # Attach Tauk data to webdriver object so that if it's quit within the test
        # we can collect necessary details before exiting
        if test_filename:
            driver.tauk_test_filename = test_filename
        if test_method_name:
            driver.tauk_test_method_name = test_method_name

        self._browser_debugger['address'] = get_browser_debugger_address(driver)
        if companion and companion.is_running() and companion.config.is_cdp_capture_enabled():
            self._connect_to_browser_debugger(companion)

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

        # This identifies the operating system at the remote-end,
        # fetching the platformName returns the OS name.
        # In cloud-based providers, setting platformName sets the OS at the remote-end.
        self.platform_name = PlatformNames.resolve(self.capabilities.get('platformName', ''))
        self.platform_version = self.capabilities.get('platformVersion', None)

        if self.capabilities.get('browserName', None):
            self.browser_name = BrowserNames.resolve(self.capabilities.get('browserName', ''))
            self.browser_version = self.capabilities.get('browserVersion', None)
            self.browser_driver_version = get_browser_driver_version(driver)

    def capture_screenshot(self):
        if self.screenshot and len(self.screenshot) > 0:
            logger.debug('Screenshot is already captured')
            return

        if not self.driver_instance:
            raise TaukException('driver object is None, check if driver is registered')

        self.screenshot = self.driver_instance.get_screenshot_as_base64()

    def capture_view_hierarchy(self):
        if self.view and len(self.view) > 0:
            logger.debug('View Hierarchy is already captured')
            return

        if not self.driver_instance:
            raise TaukException('driver object is None, check if driver is registered')

        if hasattr(self.driver_instance, 'contexts') and 'FLUTTER' in self.driver_instance.contexts:
            current_context = self.driver_instance.current_context
            self.driver_instance.switch_to.context('NATIVE_APP')
            self.view = self.driver_instance.page_source
            self.driver_instance.switch_to.context(current_context)
        else:
            self.view = self.driver_instance.page_source

    def capture_error(self, caller_filename, exec_info):
        exc_type, exc_value, exc_traceback = exec_info
        stack_summary = traceback.extract_tb(exc_traceback)

        self.error = TestError()
        self.error.error_type = exc_value.__class__.__name__
        self.error.error_msg = str(exc_value)
        self.error.traceback = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))

        for frame_summary in stack_summary:
            if caller_filename in frame_summary.filename:
                self.error.line_number = frame_summary.lineno
                self.error.invoked_func = frame_summary.name
                self.error.code_executed = frame_summary.line
                return

        logger.debug(f'Could not find a frame with filename {caller_filename} in stack summary')

    def capture_test_steps(self, testcase):
        source_lines = inspect.getsourcelines(testcase)
        starting_line_number = source_lines[1]

        output = []
        for i, line in enumerate(source_lines[0]):
            output.append({
                'line_number': starting_line_number + i,
                'line_code': line
            })

        if self.error and self.error.line_number > 0:
            for index, value in enumerate(output):
                if value['line_number'] == self.error.line_number:
                    # get previous 9 lines plus the line where the error occurred
                    # ensure that the start range value is never below zero
                    # get the next 9 lines after the error occurred
                    # ensure that the end range value never exceeds the len of the list
                    self.code_context = output[max(index - 29, 0): min(index + 30, len(output))]
                    return

        self.code_context = output

    def capture_success_data(self):
        self.status = TestStatus.PASSED

        try:
            self.capture_screenshot()
        except Exception as ex:
            logger.error('Failed to capture screenshot', exc_info=ex)

        try:
            self.capture_view_hierarchy()
        except Exception as ex:
            logger.error('Failed to capture view hierarchy', exc_info=ex)

    def capture_failure_data(self, test_filename, err, test_func):
        self.status = TestStatus.FAILED

        try:
            self.capture_screenshot()
        except Exception as ex:
            logger.error('Failed to capture screenshot', exc_info=ex)

        try:
            self.capture_view_hierarchy()
        except Exception as ex:
            logger.error('Failed to capture view hierarchy', exc_info=ex)

        try:
            self.capture_error(test_filename, err)
        except Exception as ex:
            logger.error('Failed to capture error details', exc_info=ex)

        try:
            self.capture_test_steps(testcase=test_func)
        except Exception as ex:
            logger.error('Failed to capture test steps', exc_info=ex)

    def capture_appium_logs(self):
        if not self.driver_instance:
            logger.warning('Not capturing appium logs because driver instance was not registered')
            return

        def format_appium_log(log_list):
            output = []
            for event in log_list:
                # ANSI escape sequences
                # https://bit.ly/3rK88pe
                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

                # Split at first event type occurrence
                # in square brackets, e.g. [HTTP]
                # https://bit.ly/3fItHEi
                split_log_msg = re.split(r'\[|\]', ansi_escape.sub('', event['message']), maxsplit=2)

                formatted_event = {
                    'timestamp': event.get('timestamp'),
                    'level': event.get('level'),
                    'type': split_log_msg[1],
                    'message': split_log_msg[2].strip()
                }

                output.append(formatted_event)
            return output

        # Get last 50 log entries
        # minus the 5 log entries for issuing get_log()
        slice_range = slice(-55, -5)
        self.log = format_appium_log(self.driver_instance.get_log('server')[slice_range])

    def add_attachment(self, file_path, attachment_type: AttachmentTypes):
        logger.debug(f'Adding attachment {attachment_type}: {file_path}')
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            raise TaukException(f'file not found {path}')

        # Validate file size
        size = os.path.getsize(path)
        if size > 1 << 20:  # 10 MB
            raise TaukException(f'attachment file size [{size}] cannot be greater than 10mb')

        self._attachments.append((file_path, attachment_type))
