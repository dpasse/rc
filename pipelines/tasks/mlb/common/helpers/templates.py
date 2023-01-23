from typing import Any, Dict, Tuple, List
import re


class TemplateService():
    def __init__(self) -> None:
        self.__templates = {
            '-',
            'to -',
            '- as -',
            '- at -',
            '- to -',
            '- scored',
            '- stole -',
            '- catching',
            '- at - base',
            '- at - in -',
            '- at - on -',
            '- hit for -',
            '- ran for -',
            '- safe at -',
            '- safe to -',
            '- to - on -',
            '- to - to -',
            '- hit - to -',
            '- in - field',
            '- into the -',
            '- on strikes',
            '- bunt - to -',
            '- scored on -',
            '- to (- feet)',
            '- to - on a -',
            '- hit a - to -',
            '- picked off -',
            '- pitches to -',
            'deflected by -',
            '- doubled off -',
            '- to - on the -',
            '- scored on a -',
            '- thrown - at -',
            '- to - (- feet)',
            '- pitching for -',
            '- safe at - on -',
            '- to - on - by -',
            '- to - to - to -',
            '- stretching at -',
            'caught stealing -',
            '- scored on - by -',
            '- caught stealing -',
            '- reached on - to -',
            '- reaches on - to -',
            '- struck - swinging',
            '- reached - base on -',
            '- safe at - on - by -',
            '- safe at - on a - by -',
            'advances to - on - by -',
            'out on batter interference',
            '- to - off a deflection by -',
            '- continues to at bat after - by -'
        }

    @property
    def templates(self) -> List[str]:
        return list(self.__templates)

    def clean_text(self, description: str) -> str:
        template = re.sub(r'\. *$', '', description)
        template = re.sub(r'safe at (first|second|third) and advances', 'safe at - and advances', template)
        template = re.sub(r', ((?:[A-Z.]+ |)[A-Z][\w-]+) and ([A-Z]\w+) scored', r', \g<1> scored and \g<2> scored', template)
        template = re.sub(r'by ((first|second|third) baseman|(right|left|center) fielder)', 'by - -', template)
        template = re.sub(r'by (pitcher|catcher|shortstop)', 'by -', template)

        return template

    def create_template(self, description: str, entities: Dict[str, Any]) -> str:
        template = self.clean_text(description);
        for key, value in entities.items():
            if key in ['runs', 'outs']:
                continue

            if isinstance(value, (str, int)):
                template = template.replace(str(value), '-', 1)

            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        template = self.create_template(template, item)
                    else:
                        template = template.replace(str(item), '-', 1)

        template = re.sub(r'(-( -)+)', '-', template)
        return re.sub(r' +', ' ', template).strip()

    def check_template(self, template: str) -> List[str]:
        issues = []
        for subset in (re.sub(r'[.,]+$', '', item).strip() for item in re.split(r'[,.]|\band\b', template)):
            if not subset in self.__templates:
                issues.append(subset)

        return issues

    def validate(self, description: str, entities: Dict[str, Any]) -> Tuple[bool, str]:
        template = self.create_template(description, entities)
        return not any(self.check_template(template)), template
