import os
import json

from collections import defaultdict
from prefect import flow, task


PBP_DIRECTORY = '../data/mlb/pbp/2/'

def create_graph(teams) -> dict:
    possible_outs = [0, 1, 2]

    possible_states = [
        '---',
        '1--',
        '-2-',
        '--3',
        '12-',
        '-23',
        '1-3',
        '123',
    ]

    graph = {}
    for team in teams:
        graph[team] = {
            out: {
                ''.join(map(str, state)): {
                    'runs': 0,
                    'types': defaultdict(lambda: 0)
                }
                for state in possible_states
            }
            for out in possible_outs
        }

    return graph

def slim_graph_down(graph_to_slim) -> dict:
    keys_to_delete = []
    for team in graph_to_slim.keys():
        for out in graph_to_slim[team].keys():
            for state in graph_to_slim[team][out].keys():
                total = sum(
                    graph_to_slim[team][out][state]['types'].values()
                )
                if total == 0:
                    keys_to_delete.append((team, out, state))

    for team, out, state in keys_to_delete:
        del graph_to_slim[team][out][state]

    return graph_to_slim

@task()
def generate_event_graph() -> None:
    graph = create_graph([])

    for file in os.listdir(PBP_DIRECTORY):
        file_path = os.path.join(PBP_DIRECTORY, file)
        with open(file_path, 'r', encoding='UTF8') as pbp:
            game = json.loads(pbp.read())

        for period in game['periods']:
            outs = 0
            for event in period['events']:
                if event['type'] == 'sub':
                    continue

                at_bat = event['atBat']
                bases = event['before']['bases']
                entities = event['entities']

                if not at_bat in graph:
                    graph.update(create_graph([at_bat]))

                item = graph[at_bat][outs][bases]

                item['runs'] += event['after']['runs']
                item['types'][entities['type']] += 1

                outs += event['after']['outs']

    with open('../data/mlb/pbp/computes/team_event_graph.json', 'w', encoding='UTF8') as pbp_output:
        pbp_output.write(json.dumps(slim_graph_down(graph), indent=2, sort_keys=True))

@flow(name='mlb-compute-states', persist_result=False)
def compute_states() -> None:
    generate_event_graph()


if __name__ == '__main__':
    compute_states()
