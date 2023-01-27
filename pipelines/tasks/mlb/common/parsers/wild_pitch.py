from typing import Any, Dict, Optional

import re


def handle_wild_pitch(text: str) -> Optional[Dict[str, Any]]:
    match = re.search(r'^ *(wild pitch)', text, flags=re.IGNORECASE)
    if match:
        return {
            'type': match.group(1),
        }

    return None

def handle_passed_ball(text: str) -> Optional[Dict[str, Any]]:
    match = re.search(r'^ *(passed ball)', text, flags=re.IGNORECASE)
    if match:
        return {
            'type': match.group(1),
        }

    return None
