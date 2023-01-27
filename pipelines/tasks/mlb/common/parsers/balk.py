from typing import Any, Dict, Optional

import re


def handle_balk(text: str) -> Optional[Dict[str, Any]]:
    match = re.search(r'^ *(balk)', text, flags=re.IGNORECASE)
    if match:
        return {
            'type': match.group(1)
        }

    return None
