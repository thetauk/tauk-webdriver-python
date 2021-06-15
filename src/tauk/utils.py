import re


class TestResult:
    def __init__(self, test_status=None, test_name=None, filename=None, desired_caps=None, appium_log=None, screenshot=None, page_source=None, error=None):
        self.status = test_status
        self.name = test_name
        self.filename = filename
        self.desired_caps = desired_caps
        self.log = appium_log
        self.screenshot = screenshot
        self.page_source = page_source
        self.error = error


def format_error(error_type=None, error_msg=None, line_number=None, invoked_func=None, code_executed=None):
    return {
        'errorType': error_type,
        'errorMsg': error_msg,
        'lineNumber': line_number,
        'invokedFunc': invoked_func,
        'codeExecuted': code_executed
    }


def format_appium_log(log_list):
    output = []
    for event in log_list:
        # ANSI escape sequences
        # https://bit.ly/3rK88pe
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

        # Split at first event type occurence
        # in square brackets, e.g. [HTTP]
        # https://bit.ly/3fItHEi
        split_log_msg = re.split(r'\[|\]', ansi_escape.sub(
            '', event['message']), maxsplit=2)

        formatted_event = {
            'timestamp': event.get('timestamp'),
            'level': event.get('level'),
            'type': split_log_msg[1],
            'message': split_log_msg[2].strip()
        }

        output.append(formatted_event)
    return output
