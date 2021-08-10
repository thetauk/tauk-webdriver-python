import re
import inspect
import linecache
from collections import MutableMapping


class TestResult:
    def __init__(self, test_status=None, test_name=None, filename=None, desired_caps=None, appium_log=None, screenshot=None, page_source=None, error=None, code_context=None, elapsed_time_ms=None):
        self.status = test_status
        self.name = test_name
        self.filename = filename
        self.desired_caps = desired_caps
        self.log = appium_log
        self.screenshot = screenshot
        self.page_source = page_source
        self.error = error
        self.code_context = code_context
        self.elapsed_time_ms = elapsed_time_ms


def format_error(error_type=None, error_msg=None, line_number=None, invoked_func=None, code_executed=None):
    return {
        'error_type': error_type,
        'error_msg': error_msg,
        'line_number': line_number,
        'invoked_func': invoked_func,
        'code_executed': code_executed
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


def flatten_desired_capabilities(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k

        if isinstance(v, MutableMapping):
            items.extend(flatten_desired_capabilities(
                v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def get_automation_type(desired_capabilities):
    if desired_capabilities.get('automationName'):
        return 'appium'
    elif desired_capabilities.get('browserName'):
        return 'selenium'
    else:
        return None


def calculate_elapsed_time_ms(start_time, end_time):
    return int((end_time-start_time)*1000)


def get_testcase_steps(testcase, error_line_number=0):
    testcase_source_raw = inspect.getsourcelines(testcase)
    testcase_source_clean = [step.strip() for step in testcase_source_raw[0]]
    line_number = testcase_source_raw[1]

    # Discard the initial 2 lines as they are the decorator and the testcase function name
    testcase_source_clean = testcase_source_clean[2:]
    line_number += 2

    output = []
    for step in testcase_source_clean:
        output.append(
            {
                'line_number': line_number,
                'line_code': step
            }
        )
        line_number += 1

    if error_line_number > 0:
        for index, value in enumerate(output):
            if value['line_number'] == error_line_number:
                # get previous 9 lines plus the line where the error occurred
                # ensure that the start range value is never below zero
                # get the next 9 lines after the error occured
                # ensure that the end range value never exceeds the len of the list
                result = output[max(index - 9, 0): min(index + 10, len(output))]
                return result
    else:
        return output


class FuncTracer:
    '''Usage:
    1. Create an instance
    func_tracer = FuncTracer(caller_filename)

    2. Add the function name you want to trace to the list
    func_tracer.TRACE_INTO.append(func.__name__)

    3. Pass the instance into sys.settrace
    sys.settrace(func_tracer.trace_calls)
    '''

    def __init__(self, filename):
        self.filename = filename
        self.TRACE_INTO = []
        self.EXECUTED_LINE_NUMBERS = set([])
        self.EXECUTED_STEPS = []

    def trace_lines(self, frame, event, arg):
        if event != 'line':
            return

        code_obj = frame.f_code
        func_name = code_obj.co_name
        line_no = frame.f_lineno
        filename = code_obj.co_filename

        line = linecache.getline(filename, line_no)

        if not 'print' in line.strip() and not line_no in self.EXECUTED_LINE_NUMBERS:
            self.EXECUTED_STEPS.append((line_no, line.strip()))
            self.EXECUTED_LINE_NUMBERS.add(line_no)

    def trace_calls(self, frame, event, arg):
        if event != 'call':
            return
        code_obj = frame.f_code
        func_name = code_obj.co_name
        if func_name == 'write':
            # ignore write() calls from print statements
            return

        if func_name == 'click':
            print(f'CLICK WAS CALLED ON LINE: {frame.f_back.f_lineno}')

        if func_name == 'send_keys':
            print("SEND KEYS WAS CALLED")

        if func_name == 'wait':
            print('WAIT WAS CALLED')

        line_no = frame.f_lineno
        filename = code_obj.co_filename

        # print(f"Call to {func_name} on line {line_no} of {filename}")
        if func_name in self.TRACE_INTO:
            # Trace into this function
            print(f"Call to {func_name} on line {line_no} of {filename}")
            return self.trace_lines
        return

    def trace_calls_and_returns(self, frame, event, arg):
        code_obj = frame.f_code
        func_name = code_obj.co_name
        if func_name == 'write':
            # Ignore write() calls from print statements
            return
        line_no = frame.f_lineno
        filename = code_obj.co_filename
        if event == 'call':
            print(f'Call to {func_name} on line {line_no} of {filename}')
            return self.trace_calls_and_returns
        elif event == 'return':
            print(f'{func_name} => {arg}')
        return
