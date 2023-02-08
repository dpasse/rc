from typing import Callable, List, Tuple

from . import seasons, leagues, conferences, divisions, teams


LoadersType = Callable[[str], List[str]]

_loaders: List[Tuple[str, LoadersType]] = [
    ('insert_seasons', seasons.execute),
    ('insert_leagues', leagues.execute),
    ('insert_conferences', conferences.execute),
    ('insert_divisions', divisions.execute),
    ('insert_teams', teams.execute),
]

def get_loaders() -> List[Tuple[str, LoadersType]]:
    return _loaders
