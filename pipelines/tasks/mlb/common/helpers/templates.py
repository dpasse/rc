from typing import Any, Dict, Tuple, Generator, List
import re


class TemplateService():
    def __init__(self) -> None:
        self.__templates = set([
            '- -',
            'to -',
            '- - -',
            '- at -',
            '- to -',
            '- as -',
            '- - to -',
            '- - at -',
            '- scored',
            '- stole -',
            '- - - at -',
            '- catching',
            '- to - on -',
            '- safe at -',
            '- at - base',
            '- hit for -',
            '- to - to -',
            '- ran for -',
            '- in - field',
            '- hit - to -',
            '- scored on -',
            '- bunt - to -',
            '- - at - in -',
            '- - at - on -',
            '- to - on a -',
            '- hit a - to -',
            '- pitches to -',
            '- - on strikes',
            '- doubled off -',
            '- scored on - -',
            '- thrown - at -',
            '- scored on a -',
            '- safe at - on -',
            '- to - to - to -',
            '- to - on - by -',
            '- pitching for -',
            'caught stealing -',
            '- - to - (- feet)',
            '- to - on - by - -',
            '- - stretching at -',
            '- reached on - to -',
            '- caught stealing -',
            '- to - on - by - - -',
            '- scored on - by - -',
            '- reached - base on -',
            '- scored on - by - - -',
            '- safe at - on - by - -',
            'advances to - on - by - -',
            '- safe at - on - by - - -',
        ])

    @property
    def templates(self) -> List[str]:
        return list(self.__templates)

    def create_template(self, description: str, entities: Dict[str, Any]) -> str:
        for key, value in entities.items():
            if key in ['runs', 'outs']:
                continue

            if isinstance(value, (str, int)):
                description = description.replace(str(value), '-', 1)

            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        description = self.create_template(description, item)
                    else:
                        description = description.replace(str(item), '-', 1)

        return re.sub(r' +', ' ', description).strip()

    def check_template(self, template: str) -> List[str]:
        issues = []
        for subset in (re.sub(r'[.,]+$', '', item).strip() for item in re.split(r',|\band\b', template)):
            if not subset in self.__templates:
                issues.append(subset)

        return issues

    def validate(self, description: str, entities: Dict[str, Any]) -> Tuple[bool, str]:
        template = re.sub(r'\. *$', '', description)
        template = re.sub(r'safe at (first|second|third) and advances', 'safe at - and advances', template)
        template = re.sub(r', ((?:[A-Z.]+ |)[A-Z][\w-]+) and ([A-Z]\w+) scored', r', \g<1> scored and \g<2> scored', template)
        template = re.sub(r'by ((first|second|third) baseman|(right|left|center) fielder)', 'by - -', template)
        template = re.sub(r'by (pitcher|catcher|shortstop)', 'by -', template)

        template = self.create_template(template, entities)
        return not any(self.check_template(template)), template
