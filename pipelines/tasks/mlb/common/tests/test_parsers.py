from typing import Dict, Any
import pytest
from ..helpers.parsers import EventDescriptionParser


test_data = [
    (
        'Gordon lined out to third.',
        {
            'player': 'Gordon',
            'type': 'lined out',
            'to': 'third',
            'outs': 1,
        }
    ),
    (
        'Gordon doubled to center.',
        {
            'player': 'Gordon',
            'type': 'doubled',
            'to': 'center'
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
    )
]

@pytest.mark.parametrize('description,expected', test_data)
def test_event_description_parser(description: str, expected: Dict[str, Any]):
    observation = EventDescriptionParser().transform_into_object(description)
    assert observation == expected
