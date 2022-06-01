class TestError:

    def __init__(self) -> None:
        self.error_type: str = ''
        self.error_msg: str = ''
        self.line_number: int = 0
        self.invoked_func: str = ''
        self.code_executed: str = ''

    def __getstate__(self):
        return self.__dict__
