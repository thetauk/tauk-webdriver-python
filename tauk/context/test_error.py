class TestError:
    error_type: str
    error_msg: str
    line_number: int
    invoked_func: str
    code_executed: str

    def __getstate__(self):
        return self.__dict__
