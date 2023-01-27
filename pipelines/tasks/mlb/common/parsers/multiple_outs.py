from typing import Any, Dict, Optional

import re


def handle_multiple_outs(text: str) -> Optional[Dict[str, Any]]:
    match = re.search(r'^ *(ground ball) ((?:double|triple) play)', text, flags=re.IGNORECASE)
    if match:
        return {
            'type': match.group(2),
            'how': match.group(1)
        }

    return None
