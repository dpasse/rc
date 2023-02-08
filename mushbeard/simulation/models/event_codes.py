from enum import Enum

# pylint: disable=C0103

class EventCodes(Enum):
    Strikeout = 1
    Walk = 2
    HBP = 3
    Error = 4
    LongSingle = 5
    MediumSingle = 6
    ShortSingle = 7
    ShortDouble = 8
    LongDouble = 9
    Triple = 10
    HR = 11
    GIDP = 12
    NormalGroundBall = 13
    NoAdvanceGroundBall = 14
    LineDriveInfieldFly = 15
    LongFly = 16
    MediumFly = 17
    ShortFly = 18
    ParentEvent = 100

all_event_codes = [
    EventCodes.Strikeout,
    EventCodes.Walk,
    EventCodes.HBP,
    EventCodes.Error,
    EventCodes.LongSingle,
    EventCodes.MediumSingle,
    EventCodes.ShortSingle,
    EventCodes.ShortDouble,
    EventCodes.LongDouble,
    EventCodes.Triple,
    EventCodes.HR,
    EventCodes.GIDP,
    EventCodes.NormalGroundBall,
    EventCodes.NoAdvanceGroundBall,
    EventCodes.LineDriveInfieldFly,
    EventCodes.LongFly,
    EventCodes.MediumFly,
    EventCodes.ShortFly,
]
