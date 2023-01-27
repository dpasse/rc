from typing import Any, Dict, Optional

import re


def handle_pick_off(text: str) -> Optional[Dict[str, Any]]:
    match = re.search(r'^ *.+? (picked off)', text, flags=re.IGNORECASE)
    if match:
        return {
            'type': match.group(1),
        }

    return None
