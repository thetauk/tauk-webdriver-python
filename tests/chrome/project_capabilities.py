class ProjectCapabilities:

    @staticmethod
    def base_capabilities() -> dict:
        chrome_caps = {"newCommandTimeout": 1800,
                       "browserName": "chrome",
                       "screenResolution": "1024x768"}
        return chrome_caps
