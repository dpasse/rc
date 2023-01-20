import os
import json
from typing import List
from collections import defaultdict
from prefect import flow, task

from common.helpers.extractors import get_outs_from_event
from common.pbp.models import Game, InningState


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
def generate_event_graph(games: List[Game]) -> None:
    def get_teams(games: List[Game]) -> List[str]:
        teams = []
        for game in games:
            teams.extend(game.teams)

        return set(teams)

    graph = create_graph(get_teams(games))

    for game in games:
        for period in game.periods:
            if len(period.issues) > 0:
                print(f'skipping period {period.id} in {game.id} due to {",".join(period.issues)} issue(s)...')
                continue

            state = InningState(0, [0, 0, 0])
            for event in period.events:
                skip = event.is_a('isInfoPlay') or \
                    'premature' in event.entities or \
                     not event.has_pitches

                if skip:
                    continue

                prior_state = event.get_prior_state()
                if prior_state:
                    state.add(prior_state)

                item = graph[period.at_bat]['home' if game.is_home_team(period.at_bat) else 'away'][state.outs_key][state.bases_key]
                item['runs'] += event.entities['runs'] if 'runs' in event.entities else 0
                item['types'][event.entities['type']] += 1

                result_state = event.get_result_state()
                if result_state:
                    state.add(result_state)

    with open('../data/mlb/computes/team_event_graph.json', 'w', encoding='UTF8') as pbp_output:
        pbp_output.write(json.dumps(graph, indent=2))

@task(retries=1, retry_delay_seconds=15)
def get_games() -> List[Game]:
    games: List[Game] = []
    for file in os.listdir(PBP_DIRECTORY):
        file_path = os.path.join(PBP_DIRECTORY, file)
        with open(file_path, 'r', encoding='UTF8') as pbp:
            games.append(
                Game(json.loads(pbp.read()))
            )

    return games

@flow(name='mlb-compute-states', persist_result=False)
def compute_states() -> None:
    games = get_games.submit().result()

    ## 1. event graph - team_event_graph
    generate_event_graph(games)


if __name__ == '__main__':
    compute_states()
