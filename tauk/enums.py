from enum import Enum, unique

from tauk.exceptions import TaukException


@unique
class TestStatus(Enum):
    FAILED = 'failed'
    PASSED = 'passed'
    EXCLUDED = 'excluded'

    def __getstate__(self):
        return self.value


@unique
class BrowserNames(Enum):
    CHROME = 'chrome'
    FIREFOX = 'firefox'
    EDGE = 'edge'
    SAFARI = 'safari'

    def __getstate__(self):
        return self.value

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
            raise TaukException(f'unable to resolve browser name {name}')


@unique
class AutomationTypes(Enum):
    APPIUM = 'appium'
    SELENIUM = 'selenium'
    ESPRESSO = 'espresso'
    XCTEST = 'xctest'

    def __getstate__(self):
        return self.value


@unique
class PlatformNames(Enum):
    IOS = 'ios'
    ANDROID = 'android'
    WINDOWS = 'windows'
    LINUX = 'linux'
    MACOS = 'macos'

    def __getstate__(self):
        return self.value

    @classmethod
    def resolve(cls, name: str):
        if 'mac' in name.lower():
            return PlatformNames.MACOS
        elif 'windows' in name.lower():
            return PlatformNames.WINDOWS
        elif 'linux' in name.lower():
            return PlatformNames.LINUX
        else:
            raise TaukException(f'unable to resolve platform name {name}')
