import pytest
from ..sim.state import Inning, EventCodes, InningScenario

test_data = [
    ## Strikeout
    (EventCodes.Strikeout, [0,0,0], 0, 0, [0,0,0]),
    (EventCodes.Strikeout, [1,0,0], 0, 0, [1,0,0]),
    (EventCodes.Strikeout, [1,1,0], 0, 0, [1,1,0]),
    (EventCodes.Strikeout, [1,0,1], 0, 0, [1,0,1]),
    (EventCodes.Strikeout, [0,1,1], 0, 0, [0,1,1]),
    (EventCodes.Strikeout, [0,1,0], 0, 0, [0,1,0]),
    (EventCodes.Strikeout, [0,0,1], 0, 0, [0,0,1]),
    (EventCodes.Strikeout, [1,1,1], 0, 0, [1,1,1]),

    ## Walk
    (EventCodes.Walk, [0,0,0], 0, 0, [1,0,0]),
    (EventCodes.Walk, [1,0,0], 0, 0, [1,1,0]),
    (EventCodes.Walk, [1,1,0], 0, 0, [1,1,1]),
    (EventCodes.Walk, [1,0,1], 0, 0, [1,1,1]),
    (EventCodes.Walk, [0,1,1], 0, 0, [1,1,1]),
    (EventCodes.Walk, [0,1,0], 0, 0, [1,1,0]),
    (EventCodes.Walk, [0,0,1], 0, 0, [1,0,1]),
    (EventCodes.Walk, [1,1,1], 0, 1, [1,1,1]),

    ## HBP
    (EventCodes.HBP, [0,0,0], 0, 0, [1,0,0]),
    (EventCodes.HBP, [1,0,0], 0, 0, [1,1,0]),
    (EventCodes.HBP, [1,1,0], 0, 0, [1,1,1]),
    (EventCodes.HBP, [1,0,1], 0, 0, [1,1,1]),
    (EventCodes.HBP, [0,1,1], 0, 0, [1,1,1]),
    (EventCodes.HBP, [0,1,0], 0, 0, [1,1,0]),
    (EventCodes.HBP, [0,0,1], 0, 0, [1,0,1]),
    (EventCodes.HBP, [1,1,1], 0, 1, [1,1,1]),

    ## Error
    (EventCodes.Error, [0,0,0], 0, 0, [1,0,0]),
    (EventCodes.Error, [1,0,0], 0, 0, [1,1,0]),
    (EventCodes.Error, [1,1,0], 0, 0, [1,1,1]),
    (EventCodes.Error, [1,0,1], 0, 1, [1,1,0]),
    (EventCodes.Error, [0,1,1], 0, 1, [1,0,1]),
    (EventCodes.Error, [0,1,0], 0, 0, [1,0,1]),
    (EventCodes.Error, [0,0,1], 0, 1, [1,0,0]),
    (EventCodes.Error, [1,1,1], 0, 1, [1,1,1]),

    ## Long Single
    (EventCodes.LongSingle, [0,0,0], 0, 0, [1,0,0]),
    (EventCodes.LongSingle, [1,0,0], 0, 0, [1,0,1]),
    (EventCodes.LongSingle, [1,1,0], 0, 1, [1,0,1]),
    (EventCodes.LongSingle, [1,0,1], 0, 1, [1,0,1]),
    (EventCodes.LongSingle, [0,1,1], 0, 2, [1,0,0]),
    (EventCodes.LongSingle, [0,1,0], 0, 1, [1,0,0]),
    (EventCodes.LongSingle, [0,0,1], 0, 1, [1,0,0]),
    (EventCodes.LongSingle, [1,1,1], 0, 2, [1,0,1]),

    ## Medium Single
    (EventCodes.MediumSingle, [0,0,0], 0, 0, [1,0,0]),
    (EventCodes.MediumSingle, [1,0,0], 0, 0, [1,1,0]),
    (EventCodes.MediumSingle, [1,1,0], 0, 1, [1,1,0]),
    (EventCodes.MediumSingle, [1,0,1], 0, 1, [1,1,0]),
    (EventCodes.MediumSingle, [0,1,1], 0, 2, [1,0,0]),
    (EventCodes.MediumSingle, [0,1,0], 0, 1, [1,0,0]),
    (EventCodes.MediumSingle, [0,0,1], 0, 1, [1,0,0]),
    (EventCodes.MediumSingle, [1,1,1], 0, 2, [1,1,0]),

    ## Short Single
    (EventCodes.ShortSingle, [0,0,0], 0, 0, [1,0,0]),
    (EventCodes.ShortSingle, [1,0,0], 0, 0, [1,1,0]),
    (EventCodes.ShortSingle, [1,1,0], 0, 0, [1,1,1]),
    (EventCodes.ShortSingle, [1,0,1], 0, 1, [1,1,0]),
    (EventCodes.ShortSingle, [0,1,1], 0, 1, [1,0,1]),
    (EventCodes.ShortSingle, [0,1,0], 0, 0, [1,0,1]),
    (EventCodes.ShortSingle, [0,0,1], 0, 1, [1,0,0]),
    (EventCodes.ShortSingle, [1,1,1], 0, 1, [1,1,1]),

    ## Long Double
    (EventCodes.LongDouble, [0,0,0], 0, 0, [0,1,0]),
    (EventCodes.LongDouble, [1,0,0], 0, 1, [0,1,0]),
    (EventCodes.LongDouble, [1,1,0], 0, 2, [0,1,0]),
    (EventCodes.LongDouble, [1,0,1], 0, 2, [0,1,0]),
    (EventCodes.LongDouble, [0,1,1], 0, 2, [0,1,0]),
    (EventCodes.LongDouble, [0,1,0], 0, 1, [0,1,0]),
    (EventCodes.LongDouble, [0,0,1], 0, 1, [0,1,0]),
    (EventCodes.LongDouble, [1,1,1], 0, 3, [0,1,0]),

    ## Short Double
    (EventCodes.ShortDouble, [0,0,0], 0, 0, [0,1,0]),
    (EventCodes.ShortDouble, [1,0,0], 0, 0, [0,1,1]),
    (EventCodes.ShortDouble, [1,1,0], 0, 1, [0,1,1]),
    (EventCodes.ShortDouble, [1,0,1], 0, 1, [0,1,1]),
    (EventCodes.ShortDouble, [0,1,1], 0, 2, [0,1,0]),
    (EventCodes.ShortDouble, [0,1,0], 0, 1, [0,1,0]),
    (EventCodes.ShortDouble, [0,0,1], 0, 1, [0,1,0]),
    (EventCodes.ShortDouble, [1,1,1], 0, 2, [0,1,1]),

    ## Triple
    (EventCodes.Triple, [0,0,0], 0, 0, [0,0,1]),
    (EventCodes.Triple, [1,0,0], 0, 1, [0,0,1]),
    (EventCodes.Triple, [1,1,0], 0, 2, [0,0,1]),
    (EventCodes.Triple, [1,0,1], 0, 2, [0,0,1]),
    (EventCodes.Triple, [0,1,1], 0, 2, [0,0,1]),
    (EventCodes.Triple, [0,1,0], 0, 1, [0,0,1]),
    (EventCodes.Triple, [0,0,1], 0, 1, [0,0,1]),
    (EventCodes.Triple, [1,1,1], 0, 3, [0,0,1]),

    ## HR
    (EventCodes.HR, [0,0,0], 0, 1, [0,0,0]),
    (EventCodes.HR, [1,0,0], 0, 2, [0,0,0]),
    (EventCodes.HR, [1,1,0], 0, 3, [0,0,0]),
    (EventCodes.HR, [1,0,1], 0, 3, [0,0,0]),
    (EventCodes.HR, [0,1,1], 0, 3, [0,0,0]),
    (EventCodes.HR, [0,1,0], 0, 2, [0,0,0]),
    (EventCodes.HR, [0,0,1], 0, 2, [0,0,0]),
    (EventCodes.HR, [1,1,1], 0, 4, [0,0,0]),

    ## GIDP
    (EventCodes.GIDP, [0,0,0], 0, 0, [0,0,0]), ## NA
    (EventCodes.GIDP, [1,0,0], 0, 0, [0,0,0]), ## NA
    (EventCodes.GIDP, [1,1,0], 0, 0, [1,0,0]),
    (EventCodes.GIDP, [1,0,1], 0, 1, [0,0,0]),
    (EventCodes.GIDP, [0,1,1], 0, 0, [0,1,1]), ## NA
    (EventCodes.GIDP, [0,1,0], 0, 0, [0,1,0]), ## NA
    (EventCodes.GIDP, [0,0,1], 0, 0, [0,0,1]), ## NA
    (EventCodes.GIDP, [1,1,1], 0, 0, [0,1,1]),

    ## Normal Ground Out
    (EventCodes.NormalGroundBall, [0,0,0], 0, 0, [0,0,0]),
    (EventCodes.NormalGroundBall, [1,0,0], 0, 0, [1,0,0]),
    (EventCodes.NormalGroundBall, [1,1,0], 0, 0, [1,0,1]),
    (EventCodes.NormalGroundBall, [1,0,1], 0, 1, [1,0,0]),
    (EventCodes.NormalGroundBall, [0,1,1], 0, 0, [0,1,1]),
    (EventCodes.NormalGroundBall, [0,1,0], 0, 0, [0,0,1]),
    (EventCodes.NormalGroundBall, [0,0,1], 0, 1, [0,0,0]),
    (EventCodes.NormalGroundBall, [1,1,1], 0, 1, [1,0,1]),

    ## Line Drive or Infield Fly
    (EventCodes.LineDriveInfieldFly, [0,0,0], 0, 0, [0,0,0]),
    (EventCodes.LineDriveInfieldFly, [1,0,0], 0, 0, [1,0,0]),
    (EventCodes.LineDriveInfieldFly, [1,1,0], 0, 0, [1,1,0]),
    (EventCodes.LineDriveInfieldFly, [1,0,1], 0, 0, [1,0,1]),
    (EventCodes.LineDriveInfieldFly, [0,1,1], 0, 0, [0,1,1]),
    (EventCodes.LineDriveInfieldFly, [0,1,0], 0, 0, [0,1,0]),
    (EventCodes.LineDriveInfieldFly, [0,0,1], 0, 0, [0,0,1]),
    (EventCodes.LineDriveInfieldFly, [1,1,1], 0, 0, [1,1,1]),

    ## Long Fly
    (EventCodes.LongFly, [0,0,0], 0, 0, [0,0,0]),
    (EventCodes.LongFly, [1,0,0], 0, 0, [1,0,0]),
    (EventCodes.LongFly, [1,1,0], 0, 0, [1,0,1]),
    (EventCodes.LongFly, [1,0,1], 0, 1, [1,0,0]),
    (EventCodes.LongFly, [0,1,1], 0, 1, [0,0,1]),
    (EventCodes.LongFly, [0,1,0], 0, 0, [0,0,1]),
    (EventCodes.LongFly, [0,0,1], 0, 1, [0,0,0]),
    (EventCodes.LongFly, [1,1,1], 0, 1, [1,0,1]),

    ## Medium Fly
    (EventCodes.MediumFly, [0,0,0], 0, 0, [0,0,0]),
    (EventCodes.MediumFly, [1,0,0], 0, 0, [1,0,0]),
    (EventCodes.MediumFly, [1,1,0], 0, 0, [1,1,0]),
    (EventCodes.MediumFly, [1,0,1], 0, 1, [1,0,0]),
    (EventCodes.MediumFly, [0,1,1], 0, 1, [0,1,0]),
    (EventCodes.MediumFly, [0,1,0], 0, 0, [0,1,0]),
    (EventCodes.MediumFly, [0,0,1], 0, 1, [0,0,0]),
    (EventCodes.MediumFly, [1,1,1], 0, 1, [1,1,0]),

    ## Short Fly
    (EventCodes.ShortFly, [0,0,0], 0, 0, [0,0,0]),
    (EventCodes.ShortFly, [1,0,0], 0, 0, [1,0,0]),
    (EventCodes.ShortFly, [1,1,0], 0, 0, [1,1,0]),
    (EventCodes.ShortFly, [1,0,1], 0, 0, [1,0,1]),
    (EventCodes.ShortFly, [0,1,1], 0, 0, [0,1,1]),
    (EventCodes.ShortFly, [0,1,0], 0, 0, [0,1,0]),
    (EventCodes.ShortFly, [0,0,1], 0, 0, [0,0,1]),
    (EventCodes.ShortFly, [1,1,1], 0, 0, [1,1,1]),
]

@pytest.mark.parametrize("event_code,before,outs,runs_scored,after", test_data)
def test_event_outcomes(event_code, before, outs, runs_scored, after):
    inning = Inning().load_scenario(InningScenario(bases=before, runs=0, outs=outs))
    inning.execute('test', event_code=event_code)

    last_event = inning.history[-1]
    assert last_event.runs == runs_scored, event_code
    assert last_event.bases == after, event_code
