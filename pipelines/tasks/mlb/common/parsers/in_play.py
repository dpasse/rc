import re

from .helpers import create_find_match_request, grab
from .typing import ParseType, HandleType


def handle_match(match: re.Match[str]) -> HandleType:
    return {
        'type': grab(match, 1),
    }

def parse_ground_rule_double() -> ParseType:
    expressions = [
        r'^ *(ground-rule double)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse

def parse_out_of_play_outs() -> ParseType:
    expressions = [
        r'^ *(foul (?:bunt |)(?:flyball|popfly|lineout))',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse

def parse_in_play_outs() -> ParseType:
    expressions = [
        r'^ *((?:bunt )?(?:flyball|popfly|(?:line|ground)out))',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse

def parse_in_play() -> ParseType:
    expressions = [
        r'^ *((?:intentional )?walk|hit by pitch|single|double|triple|home run)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse

def parse_fielders_choice() -> ParseType:
    expressions = [
        r"^ *(fielder's choice)",
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse

def parse_reached_on() -> ParseType:
    expressions = [
        r"^ *reached on (interference)",
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse
