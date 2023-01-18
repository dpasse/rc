from ..helpers.entities.tie_pitch_events import parse_pitch_events


def test_after_pitch_to_correct_pitch_single():
    events = [
        {
            "isScoringPlay": False,
            "isInfoPlay": True,
            "type": "after-pitch",
            "id": 24
        },
        {
            "isScoringPlay": False,
            "pitches": [
                {
                    "order": 1,
                    "prior": { "bases": [1, 0, 0] },
                    "result": {
                        "type": "strike",
                        "outcome": "foul ball",
                        "bases": [ 1, 0, 0 ]
                    },
                },
                {
                    "order": 2,
                    "prior": { "bases": [1, 0, 0] },
                    "result": {
                        "type": "ball",
                        "outcome": "ball",
                        "bases": [ 1, 0, 0 ],
                    },
                },
                {
                    "order": 3,
                    "prior": { "bases": [1, 0, 0] },
                    "result": {
                        "type": "strike",
                        "outcome": "strike looking",
                        "bases": [ 0, 0, 1 ]
                    },
                },
                {
                    "order": 4,
                    "prior": { "bases": [0, 0, 1] },
                    "result": {
                        "type": "strike",
                        "outcome": "strike swinging",
                        "bases": [ 0, 0, 1 ]
                    },
                }
            ],
            "id": 25
        }
    ]

    events = parse_pitch_events(events)

    after_pitch_event = events[0]
    assert after_pitch_event['afterPitchEvent'] == {
        'id': 25,
        'pitch': 2
    }

    assert events[1]['pitches'][1]['result']['afterPitchEvent'] == 24
    assert events[1]['pitchEvents'] == [24]

def test_after_pitch_to_correct_pitch_multiple():
    events = [
        {
            "isScoringPlay": False,
            "isInfoPlay": True,
            "type": "after-pitch",
            "id": 24
        },
        {
            "isScoringPlay": False,
            "isInfoPlay": True,
            "type": "after-pitch",
            "id": 25
        },
        {
            "isScoringPlay": False,
            "pitches": [
                {
                    "order": 1,
                    "prior": { "bases": [1, 0, 0] },
                    "result": {
                        "type": "strike",
                        "outcome": "foul ball",
                        "bases": [ 1, 0, 0 ]
                    },
                },
                {
                    "order": 2,
                    "prior": { "bases": [1, 0, 0] },
                    "result": {
                        "type": "ball",
                        "outcome": "ball",
                        "bases": [ 1, 0, 0 ],
                    },
                },
                {
                    "order": 3,
                    "prior": { "bases": [1, 0, 0] },
                    "result": {
                        "type": "strike",
                        "outcome": "strike looking",
                        "bases": [ 0, 0, 1 ],
                    },
                },
                {
                    "order": 4,
                    "prior": { "bases": [0, 0, 1] },
                    "result": {
                        "type": "strike",
                        "outcome": "strike swinging",
                        "bases": [ 0, 0, 0 ]
                    },
                },
                {
                    "order": 5,
                    "prior": { "bases": [0, 0, 0] },
                    "result": {
                        "type": "strike",
                        "outcome": "strike swinging",
                        "bases": [ 0, 0, 0 ]
                    },
                },
                {
                    "order": 6,
                    "prior": { "bases": [0, 0, 0] },
                    "result": {
                        "type": "strike",
                        "outcome": "strike swinging",
                        "bases": [ 0, 0, 0 ]
                    },
                }
            ],
            "id": 26
        }
    ]

    parse_pitch_events(events)

    assert events[0]['afterPitchEvent'] == {
        'id': 26,
        'pitch': 2
    }

    assert events[1]['afterPitchEvent'] == {
        'id': 26,
        'pitch': 3
    }

    assert events[2]['pitches'][1]['result']['afterPitchEvent'] == 24
    assert events[2]['pitches'][2]['result']['afterPitchEvent'] == 25
    assert events[2]['pitchEvents'] == [24,25]

def test_before_pitch_when_it_happens_prior_to_first_pitch():
    events = [
        {
            "isScoringPlay": False,
            "isInfoPlay": True,
            "type": "before-pitch",
            "id": 34,
        },
        {
            "isScoringPlay": False,
            "pitches": [
                {
                    "order": 1,
                    "prior": { "bases": [1, 0, 0] },
                    "result": {
                        "type": "ball",
                        "outcome": "ball",
                        "bases": [0, 0, 0],
                    },
                },
                {
                    "order": 2,
                    "prior": { "bases": [0, 0, 0] },
                    "result": {
                        "type": "ball",
                        "outcome": "ball",
                        "bases": [0, 0, 0],
                        "beforePitchEvent": 34
                    },
                },
                {
                    "order": 3,
                    "prior": { "bases": [0, 0, 0] },
                    "result": {
                        "type": "play",
                        "outcome": "line out",
                        "bases": [0, 0, 0],
                    },
                }
            ],
            "id": 35
        }
    ]

    parse_pitch_events(events)

    assert events[0]['beforePitchEvent'] == {
        'id': 35,
        'pitch': 1
    }

    assert events[1]['pitches'][0]['prior']['beforePitchEvent'] == 34
    assert events[1]['pitchEvents'] == [34]

def test_before_pitch_when_ends_inning_before_a_pitch():
    events = [
        {
            "isScoringPlay": False,
            "isInfoPlay": True,
            "type": "before-pitch",
            "id": 34,
        },
        {
          "isScoringPlay": False,
          "pitches": [],
          "id": 35
        }
    ]

    parse_pitch_events(events)

    assert events[0]['beforePitchEvent'] == {
        'id': 35
    }

    assert events[1]['pitchEvents'] == [34]
