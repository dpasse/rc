from typing import Any, Dict, Optional
import re

from .helpers import grab, create_find_match_request


def handle_match(match: re.Match[str]) -> Dict[str, Any]:
    return {
        'type': grab(match, 2),
        'how': grab(match, 1),
    }

def handle_multiple_outs() -> Optional[Dict[str, Any]]:
    expressions = [
        r'^ *(ground ball) ((?:double|triple) play)',
    ]

    return create_find_match_request(expressions, handle_match, re.IGNORECASE)
