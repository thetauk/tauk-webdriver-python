class CompanionConfig:
    def __init__(self) -> None:
        self.cdp_config = {
            'runtime': {
                'consoleLogs': {
                    'enabled': True,
                    'level': 'error',
                    'filters': ''
                },
                'exceptionLogs': {
                    'enabled': True,
                    'filters': ''
                }
            },
            'log': {
                'browserLogs': {
                    'enabled': True,
                    'level': 'error',
                    'filters': ''
                }
            },
            'network': {}
        }

    @staticmethod
    def default():
        return CompanionConfig()

    def capture_console_logs(self, capture: bool, log_level='error', filters=''):
        self.cdp_config['runtime']['consoleLogs']['enabled'] = capture
        self.cdp_config['runtime']['consoleLogs']['level'] = log_level
        self.cdp_config['runtime']['consoleLogs']['filters'] = filters

    def capture_browser_logs(self, capture: bool, log_level='error', filters=''):
        self.cdp_config['log']['browserLog']['enabled'] = capture
        self.cdp_config['log']['browserLog']['level'] = log_level
        self.cdp_config['log']['browserLog']['filters'] = filters

    def capture_uncaught_exceptions(self, capture: bool, filters=''):
        self.cdp_config['runtime']['exceptionLogs']['enabled'] = capture
        self.cdp_config['runtime']['exceptionLogs']['filters'] = filters

    def is_capturing_console_logs(self):
        return self.cdp_config['runtime']['consoleLogs']['enabled']

    def is_capturing_browser_logs(self):
        return self.cdp_config['log']['browserLog']['enabled']

    def is_capturing_uncaught_exceptions(self):
        return self.cdp_config['runtime']['exceptionLogs']['enabled']

    def is_cdp_capture_enabled(self):
        return self.is_capturing_console_logs() or \
               self.is_capturing_browser_logs() or \
               self.is_capturing_uncaught_exceptions()

    def __str__(self):
        return f'CompanionConfig: {self.cdp_config}'
