from typing import Any, Dict, Optional

import re


def handle_error(text: str) -> Optional[Dict[str, Any]]:
    match = re.search(r'^ *reached on (e\d+)', text, flags=re.IGNORECASE)
    if match:
        return {
            'type': 'Error',
        }

    return None
