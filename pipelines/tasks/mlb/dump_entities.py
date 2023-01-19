import os
import json
from prefect import flow


PBP_DIRECTORY = '../data/mlb/pbp/'
TEST_DIRECTORY = './tasks/mlb/common/tests/docs/'

@flow(name='mlb-dump-entities', persist_result=False)
def run_dump() -> None:
    keys = set()
    text_instances = []
    for file in os.listdir(PBP_DIRECTORY):
        with open(os.path.join(PBP_DIRECTORY, file), 'r', encoding='UTF8') as pbp_input:
            game = json.load(pbp_input)

        for period in game['periods']:
            for event in period['events']:

                description = event['desc']
                if not description in keys:
                    text_instances.append((description, event['entities']))
                    keys.add(description)

    with open(os.path.join(TEST_DIRECTORY, 'desc_to_entities.json'), 'w', encoding='UTF8') as test_instances:
        json.dump(text_instances, test_instances, indent=2)


if __name__ == '__main__':
    run_dump()
