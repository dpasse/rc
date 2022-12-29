mlb_id_lookup = {
    'angels': 1,
    'angels of anaheim': 1,
    'anaheim angels': 1,
    'los angeles angels of anaheim': 1,
    'los angeles angels': 1,
    'diamondbacks': 2,
    'arizona diamondbacks': 2,
    'braves': 3,
    'atlanta braves': 3,
    'orioles': 4,
    'baltimore orioles': 4,
    'red sox': 5,
    'boston red sox': 5,
    'cubs': 6,
    'chicago cubs': 6,
    'white sox': 7,
    'chicago white sox': 7,
    'reds': 8,
    'cincinnati reds': 8,
    'indians': 9,
    'guardians': 9,
    'cleveland indians': 9,
    'cleveland guardians': 9,
    'rockies': 10,
    'colorado rockies': 10,
    'tigers': 11,
    'detroit tigers': 11,
    'marlins': 12,
    'florida marlins': 12,
    'miami marlins': 12,
    'astros': 13,
    'houston astros': 13,
    'royals': 14,
    'kansas city royals': 14,
    'dodgers': 15,
    'los angeles dodgers': 15,
    'brewers': 16,
    'milwaukee brewers': 16,
    'twins': 17,
    'minnesota twins': 17,
    'expos': 18,
    'montreal expos': 18,
    'mets': 19,
    'new york mets': 19,
    'yankees': 20,
    'new york yankees': 20,
    'athletics': 21,
    'oakland athletics': 21,
    'phillies': 22,
    'philadelphia phillies': 22,
    'pirates': 23,
    'pittsburgh pirates': 23,
    'padres': 24,
    'san diego padres': 24,
    'mariners': 25,
    'seattle mariners': 25,
    'giants': 26,
    'san francisco giants': 26,
    'cardinals': 27,
    'st. louis cardinals': 27,
    'devil rays': 28,
    'rays': 28,
    'tampa bay rays': 28,
    'tampa bay devil rays': 28,
    'rangers': 29,
    'texas rangers': 29,
    'blue jays': 30,
    'toronto blue jays': 30,
    'nationals': 31,
    'washington nationals': 31,
}

class TeamNormalizer():
    def get(self, team: str) -> int:
        q = team.lower()
        if not q in mlb_id_lookup:
            raise KeyError(f'"{team}" is not supported.')

        return mlb_id_lookup[q]