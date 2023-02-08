from ..simulation.models.batters import BatterStats, BatterEventVariableFactory


def test_event_variables():
    event_variables = BatterEventVariableFactory().create(
        BatterStats('test', {
            'AB': 704, ## Appearance
            'SH': 2, ## Sac Bunts
            'SF': 3, ## Sac Flys
            'K': 63,
            'BB': 49,
            'HBP': 4,
            '1B': 225,
            '2B': 24,
            '3B': 5,
            'HR': 8
        })
    )

    output = sorted([
        (ev.event_code.value, round(ev.probability, 5))
        for ev in event_variables
    ], key=lambda ev: ev[0])

    assert output == [
        (1, 0.08268),
        (2, 0.0643),
        (3, 0.00525),
        (4, 0.01706),
        (5, 0.08858),
        (6, 0.14764),
        (7, 0.05906),
        (8, 0.0252),
        (9, 0.0063),
        (10, 0.00656),
        (11, 0.0105),
        (12, 0.13097),
        (13, 0.13097),
        (15, 0.07449),
        (16, 0.03009),
        (17, 0.07522),
        (18, 0.04513)
    ]
