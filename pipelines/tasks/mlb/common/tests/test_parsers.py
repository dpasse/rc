from typing import Dict, Any
import pytest
from ..helpers.parsers import EventDescriptionParser


test_data = [
    ## offense
    (
        'Kepler reached on infield single to third.',
        {
            'player': 'Kepler',
            'type': 'infield single',
            'at': 'third',
        }
    ),
    (
        'Kepler reached on infield single to third, Profar out at third.',
        {
            'player': 'Kepler',
            'type': 'infield single',
            'at': 'third',
            'moves': [
                {
                    'player': 'Profar',
                    'type': 'out',
                    'at': 'third'
                }
            ],
            'outs': 1
        }
    ),
    (
        'Profar reached on bunt single to third, Hosmer scored on throwing error by third baseman Ellis, Profar out stretching at third.',
        {
            'player': 'Profar',
            'type': 'bunt single',
            'at': 'third',
            'moves': [
                {
                    'player': 'Hosmer',
                    'type': 'advanced',
                    'at': 'home',
                },
                {
                    'player': 'Profar',
                    'type': 'out',
                    'at': 'third',
                }
            ],
            'outs': 1,
            'runs': 1,
        }
    ),
    (
        'Gordon doubled to center.',
        {
            'player': 'Gordon',
            'type': 'doubled',
            'at': 'center'
        }
    ),
    (
        'Gordon doubled to shallow left, Urshela scored.',
        {
            'player': 'Gordon',
            'type': 'doubled',
            'at': 'shallow left',
            'moves': [
                {
                    'player': 'Urshela',
                    'type': 'advanced',
                    'at': 'home',
                }
            ],
            'runs': 1,
        }
    ),
    (
        'Kepler reached on infield single to third.',
        {
            'player': 'Kepler',
            'type': 'infield single',
            'at': 'third',
        }
    ),
    (
        'Gordon doubled to center.',
        {
            'player': 'Gordon',
            'type': 'doubled',
            'at': 'center'
        }
    ),
    (
        'Buxton stole second.',
        {
            'player': 'Buxton',
            'type': 'stole',
            'at': 'second',
        }
    ),
    (
        'Seager to second on wild pitch by Gray, Duran to third on wild pitch by Gray.',
        {
            'player': 'Gray',
            'type': 'wild pitch',
            'moves': [
                {
                    'player': 'Seager',
                    'type': 'advanced',
                    'at': 'second',
                },
                {
                    'player': 'Duran',
                    'type': 'advanced',
                    'at': 'third',
                }
            ]
        }
    ),
    (
        'Abrams to second on passed ball by Herrera.',
        {
            'player': 'Herrera',
            'type': 'wild pitch',
            'moves': [
                {'player': 'Abrams', 'at': 'second', 'type': 'advanced'}
            ]
        }
    ),
    (
        'Cronenworth scored on Martin wild pitch, Voit to third on wild pitch by Martin.',
        {
            'type': 'wild pitch',
            'player': 'Martin',
            'moves': [
                {
                    "player": 'Cronenworth',
                    "type": 'advanced',
                    "at": 'home',
                },
                {
                    "player": 'Voit',
                    "type": 'advanced',
                    "at": 'third',
                }
            ],
            'runs': 1,
        }
    ),
    (
        'Voit scored on Martin wild pitch.',
        {
            'type': 'wild pitch',
            'player': 'Martin',
            'moves': [
                {
                    "player": 'Voit',
                    "type": 'advanced',
                    "at": 'home',
                }
            ],
            'runs': 1,
        },
    ),
    (
        'Seager walked, Semien to second.',
        {
            'player': 'Seager',
            'type': 'walked',
            'moves': [
                {'player': 'Semien', 'type': 'advanced', 'at': 'second'},
            ]
        }
    ),
    (
        'Kim hit by pitch.',
        {
            'player': 'Kim',
            'type': 'hit by pitch',
        }
    ),
    (
        'Cronenworth intentionally walked.',
        {
            'player': 'Cronenworth',
            'type': 'intentionally walked'
        }
    ),
    (
        'Hummel homered to center (439 feet), McCarthy scored and Ellis scored.',
        {
            'player': 'Hummel',
            'type': 'homered',
            'at': 'center',
            'moves': [
                {
                    'player': 'McCarthy',
                    'type': 'advanced',
                    'at': 'home'
                },
                {
                    'player': 'Ellis',
                    'type': 'advanced',
                    'at': 'home'
                },
            ],
            'runs': 3,
        }
    ),
    (
        'Profar homered to left (418 feet), Cronenworth scored, Voit scored and Myers scored.',
        {
            'player': 'Profar',
            'type': 'homered',
            'at': 'left',
            'moves': [
                {
                    'player': 'Cronenworth',
                    'type': 'advanced',
                    'at': 'home'
                },
                {
                    'player': 'Voit',
                    'type': 'advanced',
                    'at': 'home'
                },
                {
                    'player': 'Myers',
                    'type': 'advanced',
                    'at': 'home'
                },
            ],
            'runs': 4,
        }
    ),
    (
        'Hosmer scored on throwing error by third baseman Ellis',
        {
            'player': 'Hosmer',
            'type': 'throwing error',
            'at': 'home',
        }
    ),
    (
        'Cronenworth safe at first on fielding error by second baseman Marte.',
        {
            'player': 'Cronenworth',
            'type': 'fielding error',
            'at': 'first',
        }
    ),
    (
        'Cronenworth safe at first on throwing error by shortstop Perdomo.',
        {
            'player': 'Cronenworth',
            'type': 'throwing error',
            'at': 'first',
        }
    ),
    (
        'Nola hit sacrifice fly to left, Voit scored.',
        {
            'player': 'Nola',
            'type': 'sacrifice fly',
            'at': 'left',
            'moves': [
                {'player': 'Voit', 'type': 'advanced', 'at': 'home'}
            ],
            'outs': 1,
            'runs': 1,
        }
    ),
    (
        'Grisham sacrificed to pitcher, Alfaro to third.',
        {
            'player': 'Grisham',
            'type': 'sacrificed',
            'at': 'pitcher',
            'moves': [
                {'player': 'Alfaro', 'type': 'advanced', 'at': 'third'}
            ],
            'outs': 1,
        }
    ),
    (
        'Bader scored on a balk, Molina to second on a balk.',
        {
            'type': 'balk',
            'moves': [
                {'player': 'Bader', 'type': 'advanced', 'at': 'home'},
                {'player': 'Molina', 'type': 'advanced', 'at': 'second'},
            ],
            'runs': 1,
        }
    ),

    ## outs
    (
        'Gordon lined out to third.',
        {
            'player': 'Gordon',
            'type': 'lined out',
            'at': 'third',
            'outs': 1,
        }
    ),
    (
        'Heim grounded out to first.',
        {
            'player': 'Heim',
            'type': 'grounded out',
            'at': 'first',
            'outs': 1,
        }
    ),
    (
        'Cave grounded into fielder\'s choice to second, Correa out at second.',
        {
            'player': 'Cave',
            'type': 'grounded into fielder\'s choice',
            'at': 'second',
            'moves': [
                {'player': 'Correa', 'type': 'out', 'at': 'second'},
            ],
            'outs': 1,
        }
    ),
    (
        'Urshela grounded into double play, shortstop to second to first, Kepler out at second.',
        {
            'player': 'Urshela',
            'type': 'grounded into double play',
            'order': ['shortstop', 'second', 'first'],
            'moves': [
                {'player': 'Kepler', 'type': 'out', 'at': 'second'},
            ],
            'outs': 2,
        }
    ),
    (
        'Lowe lined into triple play, first to shortstop, Seager doubled off first, Semien doubled off second.',
        {
            'player': 'Lowe',
            'type': 'lined into triple play',
            'order': ['first', 'shortstop'],
            'moves': [
                {'player': 'Seager', 'type': 'out', 'at': 'first'},
                {'player': 'Semien', 'type': 'out', 'at': 'second'},
            ],
            'outs': 3,
        }
    ),
    (
        'Profar lined into double play, to first, Voit doubled off first.',
        {
            'player': 'Profar',
            'type': 'lined into double play',
            'order': ['first'],
            'moves': [
                {
                    'player': 'Voit',
                    'type': 'out',
                    'at': 'first'
                }
            ],
            'outs': 2,
        }
    ),
    (
        'Gordon caught stealing third, catcher to third.',
        {
            'player': 'Gordon',
            'type': 'caught stealing',
            'at': 'third',
            'order': ['catcher', 'third'],
            'outs': 1,
        }
    ),
    (
        'Gordon caught stealing third, catcher to third, Kepler to second.',
        {
            'player': 'Gordon',
            'type': 'caught stealing',
            'at': 'third',
            'order': ['catcher', 'third'],
            'outs': 1,
            'moves': [
                {'player': 'Kepler', 'type': 'advanced', 'at': 'second'},
            ]
        }
    ),
    (
        'Gordon caught stealing third, catcher to third, Kepler doubled off second.',
        {
            'player': 'Gordon',
            'type': 'caught stealing',
            'at': 'third',
            'order': ['catcher', 'third'],
            'outs': 2,
            'moves': [
                {'player': 'Kepler', 'type': 'out', 'at': 'second'},
            ]
        }
    ),
    (
        'Beckham struck out swinging.',
        {
            'player': 'Beckham',
            'type': 'struck out',
            'effort': 'swinging',
            'outs': 1,
        }
    ),
    (
        'Beckham struck out looking.',
        {
            'player': 'Beckham',
            'type': 'struck out',
            'effort': 'looking',
            'outs': 1,
        }
    ),

    ## subs
    (
        'S. Gray pitching for MIN',
        {
            'player': 'S. Gray',
            'type': 'sub-p',
        }
    ),
    (
        'Polanco as designated hitter.',
        {
            'player': 'Polanco',
            'type': 'sub-f',
        }
    ),
    (
        'Cave in center field.',
        {
            'player': 'Cave',
            'type': 'sub-f',
        }
    ),
    (
        'Mark Melancon pitches to Jake Cronenworth',
        {
            'player': 'Mark Melancon',
            'type': 'sub-p',
        }
    ),
    (
        'Cronenworth at third base.',
        {
            'player': 'Cronenworth',
            'type': 'sub-f',
        }
    ),
    (
        'Ted Williams ran for Jake Cronenworth',
        {
            'player': 'Ted Williams',
            'type': 'sub-f',
        }
    ),
]

@pytest.mark.parametrize('description,expected', test_data)
def test_event_description_parser(description: str, expected: Dict[str, Any]):
    observation = EventDescriptionParser().transform_into_object(description)
    assert observation == expected, observation
