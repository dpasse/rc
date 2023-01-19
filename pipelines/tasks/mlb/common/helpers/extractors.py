from typing import Dict, Any, List, Tuple


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

def get_pitch_events(events: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    pitch_events: Dict[int, Dict[str, Any]] = {}

    for event in events:
        if 'type' in event and event['type'] in ['after-pitch', 'before-pitch']:
            pitch_events[event['id']] = event

    return pitch_events

def get_game_issues(game: Dict[str, Any]) -> Dict[str, Any]:
    game_issue = {
        'id': game['id'],
        'periods': []
    }

    for period in game['periods']:
        period_issue = {
            'id': period['id'],
            'issues': period['issues'] if 'issues' in period else [],
            'events': [
                { 'id': event['id'], 'issues': event['entities']['issues'] }
                for event
                in period['events']
                if 'issues' in event['entities']
            ],
        }

        has_issues = False
        for key in ['issues', 'events']:
            has_issues = has_issues or any(period_issue[key])

        if has_issues:
            game_issue['periods'].append(period_issue)

    return game_issue

def get_outs_from_event(event: Dict[str, Any]) -> int:
    entities = event['entities']
    return entities['outs'] if 'outs' in entities else 0

def calculate_total_outs(events: List[Dict[str, Any]]) -> int:
    outs = 0
    pitch_events = get_pitch_events(events)

    for event in filter(lambda ev: not 'isInfoPlay' in ev, events):
        if 'pitchEvents' in event:
            outs += sum(
                get_outs_from_event(pitch_events[pe_id])
                for pe_id in event['pitchEvents']
            )

        outs += get_outs_from_event(event) if 'outs' in event['entities'] else 0

    return outs

def get_current_state_before_pitch(pitches: List[Dict[str, Any]], pitch_events: Dict[int, Dict[str, Any]]) -> Tuple[int, List[int]]:
    def get_pitch_event_ids(pitches):
        length = len(pitches)
        for i, pitch in enumerate(pitches[:-1]):
            prior = pitch['prior']
            if 'beforePitchEvent' in prior:
                yield prior['beforePitchEvent']

            if length != i:
                result = pitch['result']
                if 'afterPitchEvent' in result:
                    yield result['afterPitchEvent']

    outs = sum(
        get_outs_from_event(pitch_events[pe_id])
        for pe_id in get_pitch_event_ids(pitches)
    )

    return outs, (pitches[-1]['prior']['after'] if 'after' in pitches[-1]['prior'] else pitches[-1]['prior']['bases']).copy()
