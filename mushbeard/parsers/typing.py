from typing import Callable, Optional, Dict, Any
import re


MatchType = re.Match[str]
HandleType = Dict[str, Any]
OptionalHandleType = Optional[HandleType]

ParserType = Callable[[str], OptionalHandleType]
HandlerType = Callable[[MatchType], HandleType]
