from enum import Enum, unique


@unique
class TestStatus(Enum):
    FAILED = 'failed'
    PASSED = 'passed'
    EXCLUDED = 'excluded'


@unique
class BrowserNames(Enum):
    CHROME = 'Chrome'
    FIREFOX = 'Firefox'
    EDGE = 'Edge'
    SAFARI = 'Safari'


@unique
class AutomationTypes(Enum):
    APPIUM = 'Appium'
    SELENIUM = 'Selenium'
    ESPRESSO = 'Espresso'
    XCTEST = 'XCTest'


@unique
class PlatformNames(Enum):
    IOS = 'iOS'
    ANDROID = 'Android'
    WINDOWS = 'Windows'
    LINUX = 'Linux'
    MACOS = 'macOS'
