import os
import json
from typing import List, Dict, Any
from collections import defaultdict
from prefect import flow, task

from common.helpers.extractors import get_pitch_events, get_current_state_before_pitch, get_outs_from_event


PBP_DIRECTORY = '../data/mlb/pbp/'

def create_graph(teams):
    areas = ['home', 'away']

    possible_outs = ['0', '1', '2']

    possible_states = [
        [0, 0, 0],
        [1, 0, 0],
        [0, 1, 0],
        [1, 1, 0],
        [0, 0, 1],
        [1, 0, 1],
        [0, 1, 1],
        [1, 1, 1],
    ]

    graph = {}
    for team in teams:
        graph[team] = {
            area: {
                out: {
                    ''.join(map(str, state)): { 'runs': 0, 'types': defaultdict(lambda: 0) }
                    for state in possible_states
                }
                for out in possible_outs
            }
            for area in areas
        }

    return graph

def slim_graph_down(graph_to_slim):
    keys_to_delete = []
    for team in graph_to_slim.keys():
        for area in graph_to_slim[team].keys():
            for out in graph_to_slim[team][area].keys():
                for state in graph_to_slim[team][area][out].keys():
                    total = sum(graph_to_slim[team][area][out][state]['types'].values())
                    if total == 0:
                        keys_to_delete.append((team, area, out, state))

    for team, area, out, state in keys_to_delete:
        del graph_to_slim[team][area][out][state]

    return graph_to_slim

@task(retries=1, retry_delay_seconds=15)
def generate_event_graph(games: List[Dict[str, Any]]) -> None:
    def get_teams(games: List[Dict[str, Any]]) -> List[str]:
        teams = set([])
        for game in games:
            teams.add(game['home'])
            teams.add(game['away'])

        return teams

    graph = create_graph(
        get_teams(games),
    )

    for game in games:
        team_lookup = { game['home']: 'home', game['away']: 'away' }

        for period in game['periods']:
            if 'issues' in period:
                print(f'skipping period {period["id"]} in {game["id"]} due to {period["issues"]} issue(s)...')
                continue

            state = { 'outs': 0, 'bases': [0, 0, 0] }
            pitch_events = get_pitch_events(period['events'])

            for event in period['events']:
                if 'isInfoPlay' in event:
                    continue

                entities = event['entities']
                if 'premature' in entities:
                    ## ie. player caught stealing to end the inning
                    continue

                pitches = event['pitches']
                if len(pitches) == 0:
                    continue

                ## prior to the last pitch
                outs_before, bases_before = get_current_state_before_pitch(pitches, pitch_events)
                state['outs'] += outs_before
                state['bases'] = bases_before.copy()

                team = period['atBat']
                location = team_lookup[team]
                outs = str(state['outs'])
                bases = ''.join(map(str, state['bases']))

                item = graph[team][location][outs][bases]
                item['runs'] += entities['runs'] if 'runs' in entities else 0
                item['types'][entities['type']] += 1

                result = pitches[-1]['result']
                if 'afterPitchEvent' in result:
                    state['outs'] += get_outs_from_event(pitch_events[result['afterPitchEvent']])

                state['outs'] += get_outs_from_event(event)
                state['bases'] = result['bases'].copy()

    with open('../data/mlb/computes/team_event_graph.json', 'w', encoding='UTF8') as pbp_output:
        pbp_output.write(json.dumps(graph, indent=2))

@task(retries=1, retry_delay_seconds=15)
def get_games() -> List[Dict[str, Any]]:
    games = []
    for file in os.listdir(PBP_DIRECTORY):
        file_path = os.path.join(PBP_DIRECTORY, file)
        with open(file_path, 'r', encoding='UTF8') as pbp:
            games.append(
                json.loads(pbp.read())
            )

    return games

@flow(name='mlb-compute-states', persist_result=False)
def compute_states() -> None:
    games = get_games.submit().result()

    ## 1. event graph - team_event_graph
    generate_event_graph(games)


if __name__ == '__main__':
    compute_states()
