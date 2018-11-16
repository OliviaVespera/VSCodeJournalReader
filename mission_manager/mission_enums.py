from enum import Enum

class MissionStatus(Enum):
    Not_Started = 1
    Started = 2
    Completed = 3
    Failed = 4
    Cancelled = 5


class Conditional_Syle(Enum):
    Hold_and_Fail = 0
    Hold_and_Victory = 1
    Toggle_and_Fail = 2
    Toggle_and_Victory = 4


class NodeType(Enum):
    Beginning = 1
    Middle = 2
    End = 3