import re

from ..helpers import grab_match_group
from ..models import create_find_match_request
from ..typing import ParserType, HandleType, MatchType


def handle_match(match: MatchType) -> HandleType:
    return {
        'type': grab_match_group(match, 1),
    }

def parse_ground_rule_double() -> ParserType:
    expressions = [
        r'^ *(ground-rule double)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse

def parse_flyball() -> ParserType:
    expressions = [
        r'^ *(bunt flyball)',
        r'^ *(foul(?:bunt| )+flyball)',
        r'^ *(flyball)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse

def parse_popfly() -> ParserType:
    expressions = [
        r'^ *(bunt popfly)',
        r'^ *(foul(?:bunt| )+popfly)',
        r'^ *(popfly)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse

def parse_lineout() -> ParserType:
    expressions = [
        r'^ *(bunt lineout)',
        r'^ *(foul(?:bunt| )+lineout)',
        r'^ *(lineout)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse

def parse_groundout() -> ParserType:
    expressions = [
        r'^ *(bunt groundout)',
        r'^ *(foul(?:bunt| )+groundout)',
        r'^ *(groundout)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse


def parse_single() -> ParserType:
    expressions = [
        r'^ *(single)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse

def parse_double() -> ParserType:
    expressions = [
        r'^ *(double)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse

def parse_triple() -> ParserType:
    expressions = [
        r'^ *(triple)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse

def parse_hit_by_pitch() -> ParserType:
    expressions = [
        r'^ *(hit by pitch)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse

def parse_walk() -> ParserType:
    expressions = [
        r'^ *(intentional walk|walk)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse

def parse_homerun() -> ParserType:
    expressions = [
        r'^ *(home run|inside-the-park home run)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse

def parse_fielders_choice() -> ParserType:
    expressions = [
        r"^ *(fielder's choice)",
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse

def parse_reached_on() -> ParserType:
    expressions = [
        r"^ *reached on (interference)",
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE).parse
