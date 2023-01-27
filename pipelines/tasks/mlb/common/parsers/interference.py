from typing import Any, Dict, Optional

import re


def handle_interference(text: str) -> Optional[Dict[str, Any]]:
    match = re.search(r'^ *(bunt Interference)', text, flags=re.IGNORECASE)
    if match:
        return {
            'type': match.group(1)
        }

    return None
