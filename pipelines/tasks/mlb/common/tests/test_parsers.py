from typing import Dict, Any
import json
import pytest
from ..helpers.parsers import EventDescriptionParser


test_data = []
with open('./tasks/mlb/common/tests/docs/desc_to_entities.json', 'r', encoding='UTF8') as file_input:
    test_data = json.load(file_input)


@pytest.mark.parametrize('description,expected', test_data)
def test_event_description_parser(description: str, expected: Dict[str, Any]):
    observation = EventDescriptionParser().transform_into_object(description)
    assert observation == expected, observation
