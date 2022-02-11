from enum import Enum, unique


@unique
class TestStatus(Enum):
    FAILED = 'failed'
    PASSED = 'passed'
    EXCLUDED = 'excluded'


@unique
class BrowserNames(Enum):
    CHROME = 'chrome'
    FIREFOX = 'firefox'
    EDGE = 'edge'
    SAFARI = 'safari'


@unique
class AutomationTypes(Enum):
    APPIUM = 'appium'
    SELENIUM = 'selenium'


@unique
class PlatformTypes(Enum):
    IOS = 'ios'
    ANDROID = 'android'
    WINDOWS = 'windows'
    LINUX = 'linux'
    OSX = 'osx'
