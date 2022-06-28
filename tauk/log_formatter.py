from datetime import datetime, timezone

from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):

    def __init__(self, *args, **kwargs):
        # Check and store context so that we can extract the test method name
        if kwargs.get('tauk_context'):
            self.ctx = kwargs.get('tauk_context')
            kwargs.pop('tauk_context')

        super().__init__(*args, **kwargs)

    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            # this doesn't use record.created, so it is slightly off
            log_record['timestamp'] = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname

        if self.ctx and self.ctx.test_data:
            # Iterate and find the suite with one testcase in it because
            # testcase gets cleand up after its over but suites does not
            # TODO: Make this implementation thread safe
            for suite in self.ctx.test_data.test_suites:
                if len(suite.test_cases) == 1:
                    log_record['suite'] = suite.filename
                    log_record['test'] = suite.test_cases[0].method_name
