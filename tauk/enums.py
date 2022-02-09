from enum import Enum

class TestStatusType(Enum):
    failed = 0
    passed = 1
    excluded = 2
    resolved = 3
    undetermined = 4