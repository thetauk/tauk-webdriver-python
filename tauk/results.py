import time

from tauk.enums import TestStatus, BrowserNames, AutomationTypes, PlatformTypes


class TaukTestResults:
    _test_status: TestStatus = None
    _automation_type: AutomationTypes = None  # TODO: determine correct way to get automation type
    _language = 'Python'
    _platform: PlatformTypes = None
    _platform_version: str = None
    _browser_name: BrowserNames = None
    _browser_version: str = None
    _test_start_time: float = None
    _test_end_time: float = None
    _timezone: str = None
    _error = None
    _screenshot = None
    _view = None
    _code_context = None
    _user_data = {}

    def __init__(self, test_name, test_file_name) -> None:
        self._test_name = test_name
        # test_file_name format my.package.name.test_file_name
        self._test_file_name = test_file_name
        self._timezone = time.tzname[time.daylight if time.localtime().tm_isdst != 0 else 0]

    @property
    def test_status(self):
        return self._test_status

    @test_status.setter
    def test_status(self, test_status):
        self._test_status = test_status

    @property
    def automation_type(self):
        return self._automation_type

    @automation_type.setter
    def automation_type(self, automation_type):
        self._automation_type = automation_type

    @property
    def language(self):
        return self._language

    @property
    def platform(self):
        return self._platform

    @platform.setter
    def platform(self, platform):
        self._platform = platform

    @property
    def platform_version(self):
        return self._platform_version

    @platform_version.setter
    def platform_version(self, platform_version):
        self._platform_version = platform_version

    @property
    def browser_name(self):
        return self._browser_name

    @browser_name.setter
    def browser_name(self, browser_name):
        self._browser_name = browser_name

    @property
    def browser_version(self):
        return self._automation_type

    @browser_version.setter
    def browser_version(self, browser_version):
        self._browser_version = browser_version

    @property
    def test_start_time(self):
        return self._test_start_time

    @test_start_time.setter
    def test_start_time(self, test_start_time):
        self._test_start_time = test_start_time

    @property
    def test_end_time(self):
        return self._test_end_time

    @test_end_time.setter
    def test_end_time(self, test_end_time):
        self._test_end_time = test_end_time

    @property
    def timezone(self):
        return self._timezone

    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, error):
        exc_value, line_number, invoked_func, code_executed = error
        self._error = {
            'error_type': str(exc_value.__class__.__name__),
            'error_msg': str(exc_value),
            'line_number': int(line_number),
            'invoked_func': invoked_func,
            'code_executed': code_executed
        }

    @property
    def screenshot(self):
        return self._screenshot

    @screenshot.setter
    def screenshot(self, screenshot):
        self._screenshot = screenshot

    @property
    def view(self):
        return self._view

    @view.setter
    def view(self, view):
        self._view = view @ property

    @property
    def code_context(self):
        return self._code_context

    @code_context.setter
    def code_context(self, code_context):
        self._code_context = code_context

    @property
    def user_data(self):
        return self._user_data

    @user_data.setter
    def user_data(self, user_data):
        self._user_data = user_data

    def to_json(self):
        return {
            "test_status": self.test_status,
            "automation_type": self.automation_type,
            "language": self.language,
            "platform": self.platform,
            "platform_version": self.platform_version,
            "browser_name": self.browser_name,
            "browser_version": self.browser_version,
            "test_start_time": self.test_start_time,
            "test_end_time": self.test_end_time,
            "timezone": self.timezone,
            "error": self.error,
            "screenshot": self.screenshot,
            "view": self.view,
            "code_context": self.code_context,
            "user_data": self.user_data
        }
