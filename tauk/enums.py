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
    COMPANION_CONSOLE_LOGS = 'Runtime.consoleLogs'
    COMPANION_EXCEPTION_LOGS = 'Runtime.exceptionLogs'
    COMPANION_BROWSER_LOGS = 'Log.browserLogs'

    @classmethod
    def resolve_companion_log(cls, name: str):
        if 'console_logs.json' in name.lower():
            return AttachmentTypes.COMPANION_CONSOLE_LOGS
        elif 'exception_logs.json' in name.lower():
            return AttachmentTypes.COMPANION_EXCEPTION_LOGS
        elif 'browser_logs.json' in name.lower():
            return AttachmentTypes.COMPANION_BROWSER_LOGS
        else:
            raise TaukException(f'unable to resolve platform name {name}')

    @classmethod
    def is_companion_attachment(cls):
        if cls.name in [AttachmentTypes.COMPANION_EXCEPTION_LOGS,
                        AttachmentTypes.COMPANION_EXCEPTION_LOGS,
                        AttachmentTypes.COMPANION_BROWSER_LOGS]:
            return True

        return False
