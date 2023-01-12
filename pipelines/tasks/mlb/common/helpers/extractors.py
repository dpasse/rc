from typing import Dict, Any


def get_pitchers_first_appearance(data: dict) -> Dict[str, Dict[str, int]]:
    teams = [
        data['away'],
        data['home']
    ]

    def get_pitching_team(at_bat: str) -> str:
        return list(filter(lambda team: team != at_bat, teams))[0]

    pitchers_first_appearance: Dict[str, Dict[str, int]] = {
        team: {}
        for team in teams
    }

    for period in data['periods']:
        pitching_team = get_pitching_team(period['atBat'])
        for event in period['events']:
            if 'entities' in event and event['entities']['type'] == 'sub-p':
                pitcher = event['entities']['player']

                has_already_appeared = pitcher in pitchers_first_appearance[pitching_team]
                if not has_already_appeared:
                    pitchers_first_appearance[pitching_team][pitcher] = event['id']

    return pitchers_first_appearance

def get_pitch_events(data: dict) -> Dict[int, Dict[str, Any]]:
    after_pitch_events: Dict[int, Dict[str, Any]] = {}

    for period in data['periods']:
        for event in period['events']:
            if 'type' in event and event['type'] in ['after-pitch', 'before-pitch']:
                after_pitch_events[event['id']] = event

    return after_pitch_events