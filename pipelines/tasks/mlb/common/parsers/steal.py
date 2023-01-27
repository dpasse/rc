from typing import Any, Dict, Optional

import re


def handle_steal(text: str) -> Optional[Dict[str, Any]]:
    match = re.search(r'^ *.+? (steals) (.+)', text, flags=re.IGNORECASE)
    if match:
        return {
            'type': match.group(1),
            'at': match.group(2)
        }

    return None

def handle_caught_stealing(text: str) -> Optional[Dict[str, Any]]:
    match = re.search(r'^ *(.+?) (caught stealing)', text, flags=re.IGNORECASE)
    if match:
        return {
            'type': match.group(1),
            'at': match.group(2)
        }

    return None
