import logging
from enum import Enum, unique

from tauk.exceptions import TaukException

logger = logging.getLogger('tauk')


@unique
class TaukEnum(Enum):
    def __getstate__(self):
        return self.value


@unique
class TestStatus(TaukEnum):
    FAILED = 'failed'
    PASSED = 'passed'
    EXCLUDED = 'excluded'


@unique
class BrowserNames(TaukEnum):
    CHROME = 'chrome'
    FIREFOX = 'firefox'
    EDGE = 'edge'
    SAFARI = 'safari'

    @classmethod
    def resolve(cls, name: str):
        if 'chrome' in name.lower():
            return BrowserNames.CHROME
        elif 'firefox' in name.lower():
            return BrowserNames.FIREFOX
        elif 'edge' in name.lower():
            return BrowserNames.EDGE
        elif 'safari' in name.lower():
            return BrowserNames.SAFARI
        else:
            logger.warning(f'Unsupported browser name {name}')


@unique
class AutomationTypes(TaukEnum):
    APPIUM = 'appium'
    SELENIUM = 'selenium'
    ESPRESSO = 'espresso'
    XCTEST = 'xctest'


@unique
class PlatformNames(TaukEnum):
    IOS = 'ios'
    ANDROID = 'android'
    WINDOWS = 'windows'
    LINUX = 'linux'
    MACOS = 'macos'

    @classmethod
    def resolve(cls, name: str):
        if 'mac' in name.lower():
            return PlatformNames.MACOS
        elif 'windows' in name.lower():
            return PlatformNames.WINDOWS
        elif 'linux' in name.lower():
            return PlatformNames.LINUX
        elif 'android' in name.lower():
            return PlatformNames.ANDROID
        elif 'ios' in name.lower():
            return PlatformNames.IOS
        else:
            raise TaukException(f'unable to resolve platform name {name}')


@unique
class AttachmentTypes(TaukEnum):
    ASSISTANT_CONSOLE_LOGS = 'Runtime.consoleLogs'
    ASSISTANT_EXCEPTION_LOGS = 'Runtime.exceptionLogs'
    ASSISTANT_BROWSER_LOGS = 'Log.browserLogs'

    @classmethod
    def resolve_assistant_log(cls, name: str):
        if 'console_logs.json' in name.lower():
            return AttachmentTypes.ASSISTANT_CONSOLE_LOGS
        elif 'exception_logs.json' in name.lower():
            return AttachmentTypes.ASSISTANT_EXCEPTION_LOGS
        elif 'browser_logs.json' in name.lower():
            return AttachmentTypes.ASSISTANT_BROWSER_LOGS
        else:
            raise TaukException(f'unable to resolve platform name {name}')

    @classmethod
    def is_assistant_attachment(cls, attachment_type):
        if attachment_type in [AttachmentTypes.ASSISTANT_EXCEPTION_LOGS,
                               AttachmentTypes.ASSISTANT_EXCEPTION_LOGS,
                               AttachmentTypes.ASSISTANT_BROWSER_LOGS]:
            return True

        return False
