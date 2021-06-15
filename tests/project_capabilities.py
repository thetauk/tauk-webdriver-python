class ProjectCapabilities:

    @staticmethod
    def android_base_capabilities() -> dict:
        android_caps = {"newCommandTimeout": 1800,
                        "deviceName": "Android Emulator",
                        "platformName": "Android",
                        "automationName": "UiAutomator2",
                        "appPackage": "com.android.settings",
                        "appActivity": ".Settings",
                        "autoAcceptAlerts": True}
        return android_caps

    @staticmethod
    def ios_base_caps() -> dict:
        ios_caps = {"newCommandTimeout": 1800,
                    "deviceName": "iPhone 12 Pro Max",
                    "automationName": "XCUITest",
                    "platformVersion": "14.3",
                    "platformName": "iOS",
                    "bundleId": "com.apple.Preferences"}
        return ios_caps
