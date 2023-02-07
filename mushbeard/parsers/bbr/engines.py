from typing import List, Tuple
import pandas as pd

from . import get_parsers
from ..typing import HandleType
from ..models import Phrase, create_play_by_play_description_parser


EVENT_START = 'e-start'
EVENT_END = 'e-end'

class PlayByPlayParser():
    def __init__(self) -> None:
        self.__description_parser = create_play_by_play_description_parser(
            get_parsers()
        )

    @staticmethod
    def get_break_points(df: pd.DataFrame) -> List[Tuple[int, int]]:
        return list(zip(
            df[df.Inn == EVENT_START].index.values,
            df[df.Inn == EVENT_END].index.values
        ))

    @staticmethod
    def to_parent_child_relationship(events: List[HandleType]) -> List[HandleType]:
        batter = ''
        previous_events: List[HandleType] = []

        in_play_events: List[HandleType] = []

        for event in events:
            if event['type'] == 'sub':
                in_play_events.append(event)

            elif event['batter'] == batter:
                previous_events.append(event)

            else:
                length = len(previous_events)
                if length > 0:
                    last_event = previous_events[-1]

                    if length > 1:
                        last_event['before']['events'] = []
                        for previous_event in previous_events[:-1]:
                            previous_event['beforeEvent'] = last_event['id']
                            last_event['before']['events'].append(previous_event)

                    in_play_events.append(last_event)

                batter = event['batter']
                previous_events = [event]

        length = len(previous_events)
        if length > 0:
            last_event = previous_events[-1]

            if length > 1:
                last_event['before']['events'] = []
                for previous_event in previous_events[:-1]:
                    previous_event['beforeEvent'] = last_event['id']
                    last_event['before']['events'].append(previous_event)

            in_play_events.append(last_event)

        return in_play_events

    def parse(self, df: pd.DataFrame) -> List[HandleType]:
        inning = 0
        event_identifier = 1
        periods: List[HandleType] = []

        break_points = enumerate(
            df.iloc[s+1:e].copy()
            for s, e
            in PlayByPlayParser.get_break_points(df)
        )

        for i, df_subset in break_points:
            is_top = (i + 1) % 2 == 1

            inning += int(is_top)

            df_subset['RoB'] = df['RoB'].bfill()

            rob = df_subset.RoB.tolist()
            df_subset['aRoB'] = rob[1:] + rob[-1:]
            df_subset['aRoB'] = df_subset['aRoB'].astype(str)

            events: List[HandleType] = []
            for _, row in df_subset.iterrows():
                event = {
                    'id': event_identifier,
                    'desc': row['Play Description']
                }

                if isinstance(row['id'], str):
                    rob = str(row['RoB'])
                    arob = str(row['aRoB'])

                    event.update({
                        'type': 'at-bat',
                        'atBat': row['@Bat'],
                        'pitcher': row['Pitcher'],
                        'batter': row['Batter'],
                        'before': {
                            'bases': rob,
                        },
                        'after': {
                            'outs': row['R/O'].count('O'),
                            'runs': row['R/O'].count('R'),
                            'bases': arob,
                            'pitches': row['Pit(cnt)'],
                        },
                        'entities': self.__description_parser.parse(Phrase(row['Play Description'])),
                    })

                    if event['entities'] is None:
                        raise ValueError(f'could not parse "{row["Play Description"]}".')

                else:
                    event.update({
                        'type': 'sub',
                    })

                events.append(event)
                event_identifier += 1

            periods.append({
                'id': i + 1,
                'inning': f'{"top" if is_top else "bottom"}-{inning}',
                'events': PlayByPlayParser.to_parent_child_relationship(events)
            })

        return periods
