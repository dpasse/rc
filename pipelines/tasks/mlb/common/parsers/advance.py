from typing import Any, Dict, Optional

import re


def handle_advance(text: str) -> Optional[Dict[str, Any]]:
    match = re.search(r'^ *(.+?) to ([123]B) *$', text)
    if match:
        return {
            'player': match.group(1),
            'type': 'Advanced',
            'at': match.group(2)
        }

    return None

def handle_out_advance(text: str) -> Optional[Dict[str, Any]]:
    match = re.search(r'^ *baserunner (out advancing) *$', text, flags=re.IGNORECASE)
    if match:
        return {
            'type': match.group(1)
        }

    return None
