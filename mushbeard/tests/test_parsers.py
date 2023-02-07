from typing import Dict, Any, List

import pytest
from ..parsers.models import PlayByPlayDescriptionParser, Phrase
from ..parsers.bbr import get_parsers


test_data: List[Dict[str, Any]] = []

##if len(test_data) == 0:
##   with open('./tasks/mlb/common/tests/docs/desc_to_entities.json', 'r', encoding='UTF8') as file_input:
##       test_data = json.load(file_input)


@pytest.mark.parametrize('description,expected', test_data)
def test_event_description_parser(description: str, expected: Dict[str, Any]):
    observation = PlayByPlayDescriptionParser(get_parsers()).parse(Phrase(description))

    if len(test_data) == 1:
        print(observation)

    assert observation == expected, observation
