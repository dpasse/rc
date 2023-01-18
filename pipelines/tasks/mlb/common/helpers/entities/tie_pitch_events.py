from typing import List, Dict, Any, Optional, cast


DELTA_KEY = 'delta'
BEFORE_PITCH_EVENT = 'beforePitchEvent'
AFTER_PITCH_EVENT = 'afterPitchEvent'

def clear_pitch(pitch: Dict[str, Any]) -> Dict[str, Any]:
    if 'result' in pitch:
        for key in [AFTER_PITCH_EVENT, BEFORE_PITCH_EVENT, DELTA_KEY]:
            if key in pitch['result']:
                del pitch['result'][key]

    if 'prior' in pitch:
        for key in [AFTER_PITCH_EVENT, BEFORE_PITCH_EVENT, DELTA_KEY]:
            if key in pitch['prior']:
                del pitch['prior'][key]

    return pitch

def clear_event(event: Dict[str, Any]) -> Dict[str, Any]:
    for key in ['pitchEvents', BEFORE_PITCH_EVENT, AFTER_PITCH_EVENT]:
        if key in event:
            del event[key]

    return event

def set_pitch_deltas(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for event in events:
        clear_event(event)

        if 'isInfoPlay' in event:
            continue

        if 'pitches' in event:
            number_of_pitches = len(event['pitches'])
            for i, current_pitch in enumerate(event['pitches']):

                current_pitch = clear_pitch(current_pitch)

                if i < number_of_pitches - 1:
                    if current_pitch['prior']['bases'] != current_pitch['result']['bases']:
                        current_pitch['result'][DELTA_KEY] = True

    return events

def tie_pitch_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    pitch_events: List[Dict[str, Any]] = []
    for event in events:
        is_info_event = 'isInfoPlay' in event

        if 'type' in event:
            if event['type'] in ['after-pitch', 'before-pitch']:
                pitch_events.append(event)

        elif not is_info_event and len(pitch_events) > 0:
            pitch_event_observation = {
                'id': event['id'],
            }

            event['pitchEvents'] = []

            pitch_event, pitch_events = pitch_events[0], pitch_events[1:]

            pitches = cast(
                List[Dict[str, Any]],
                event['pitches'] if 'pitches' in event else []
            )

            if len(pitches) == 0 and pitch_event['type'] == 'before-pitch':
                pitch_event[BEFORE_PITCH_EVENT] = pitch_event_observation.copy()
                event['pitchEvents'].append(pitch_event['id'])
            else:
                for i, pitch in enumerate(pitches):
                    is_last_pitch = i == len(pitches) - 1
                    if not (DELTA_KEY in pitch['result'] or is_last_pitch):
                        continue

                    key = AFTER_PITCH_EVENT if pitch_event['type'] == 'after-pitch' else BEFORE_PITCH_EVENT

                    if key == BEFORE_PITCH_EVENT:
                        ## use current pitch
                        pitch_event_observation['pitch'] = pitch['order']
                        pitch['prior'][key] = pitch_event['id']

                    if key == AFTER_PITCH_EVENT:
                        ## use previous pitch
                        pitch_to_use = pitch if is_last_pitch else pitches[i-1]
                        pitch_event_observation['pitch'] = pitch_to_use['order']
                        pitch_to_use['result'][key] = pitch_event['id']

                    pitch_event[key] = pitch_event_observation.copy()
                    event['pitchEvents'].append(pitch_event['id'])

                    if len(pitch_events) == 0:
                        break

                    pitch_event, pitch_events = pitch_events[0], pitch_events[1:]

            if len(pitch_events) > 0:
                print()
                print('NOT ALL PITCH EVENTS COULD BE ACCOUNTED FOR!!')
                print()

            pitch_events.clear()

    return events

def parse_pitch_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    events = set_pitch_deltas(events)
    events = tie_pitch_events(events)

    return events
