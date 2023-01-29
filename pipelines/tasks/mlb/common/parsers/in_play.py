from typing import Any, Dict
import re

from .helpers import grab, create_find_match_request, FindMatch


def handle_match(match: re.Match[str]) -> Dict[str, Any]:
    return {
        'type': grab(match, 1),
    }

def handle_ground_rule_double() -> FindMatch:
    expressions = [
        r'^ *(ground-rule double)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE)

def handle_out_of_play_outs() -> FindMatch:
    expressions = [
        r'^ *(foul (?:bunt |)(?:flyball|popfly|lineout))',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE)

def handle_in_play_outs() -> FindMatch:
    expressions = [
        r'^ *((?:bunt )?(?:flyball|popfly|(?:line|ground)out))',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE)

def handle_in_play() -> FindMatch:
    expressions = [
        r'^ *((?:intentional )?walk|hit by pitch|single|double|triple|home run)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE)

def handle_fielders_choice() -> FindMatch:
    expressions = [
        r"^ *(fielder's choice)",
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE)

def handle_reached_on() -> FindMatch:
    expressions = [
        r"^ *reached on (interference)",
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE)
