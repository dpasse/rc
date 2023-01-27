from typing import Any, Dict, Optional

import re


def handle_strikeout(text: str) -> Optional[Dict[str, Any]]:
    match = re.search(r'^ *(strikeout) (swinging|looking)', text, flags=re.IGNORECASE)
    if match:
        return {
            'type': match.group(1),
            'how': match.group(2)
        }

    return None
