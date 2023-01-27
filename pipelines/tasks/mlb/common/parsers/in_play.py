from typing import Any, Dict, Optional

import re


def handle_ground_rule_double(text: str) -> Optional[Dict[str, Any]]:
    match = re.search(r'^ *(ground-rule double)', text, flags=re.IGNORECASE)
    if match:
        return {
            'type': match.group(1)
        }

    return None

def handle_out_of_play_outs(text: str) -> Optional[Dict[str, Any]]:
    match = re.search(r'^ *(foul) ((?:bunt |)(?:flyball|popfly|lineout))', text, flags=re.IGNORECASE)
    if match:
        return {
            'type': match.group(2)
        }

    return None

def handle_in_play_outs(text: str) -> Optional[Dict[str, Any]]:
    match = re.search(r'^ *((?:bunt )?(?:flyball|popfly|(?:line|ground)out))', text, flags=re.IGNORECASE)
    if match:
        return {
            'type': match.group(0)
        }

    return None

def handle_in_play(text: str) -> Optional[Dict[str, Any]]:
    match = re.search(r'^ *((?:intentional )?walk|hit by pitch|single|double|triple|home run)', text, flags=re.IGNORECASE)
    if match:
        return {
            'type': match.group(0)
        }

    return None

def handle_fielders_choice(text: str) -> Optional[Dict[str, Any]]:
    match = re.search(r"^ *(fielder's choice)", text, flags=re.IGNORECASE)
    if match:
        return {
            'type': match.group(0)
        }

    return None

def handle_reached_on(text: str) -> Optional[Dict[str, Any]]:
    match = re.search(r"^ *reached on (interference)", text, flags=re.IGNORECASE)
    if match:
        return {
            'type': match.group(0)
        }

    return None