from typing import Callable, Optional, Dict, Any


HandleType = Dict[str, Any]
OptionalHandleType = Optional[HandleType]
ParseType = Callable[[str], OptionalHandleType]
