from enum import Enum

class EventStatus(str, Enum):
    #    (Pending, Started, Ended or Cancelled)
    PENDING = "PENDING"
    STARTED = "STARTED"
    ENDED = "ENDED"
    CANCELLED = "CANCELLED"

class EventType(str, Enum):
    PREPLAY = "PREPLAY"
    INPLAY = "INPLAY"

class SelectionOutcome(str, Enum):
    # Outcome (Unsettled, Void, Lose or Win)
    UNSETTLED = "UNSETTLED"
    VOID = "VOID"
    LOSE = "LOSE"
    WIN = "WIN"