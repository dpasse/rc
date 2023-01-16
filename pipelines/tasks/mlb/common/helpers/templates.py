from typing import Any, Dict, Tuple
import re


class TemplateService():
    def __init__(self) -> None:
        self.__templates = [
            '- -',
            '- - -',
            '- as -',
            '- at -',
            '- - to -',
            '- catching',
            '- ran for -',
            '- to - on -',
            '- at - base',
            '- hit for -',
            '- -, - to -',
            '- in - field',
            '- bunt - to -',
            '- - -, - to -',
            '- to - on a -',
            '- - at - on -',
            '- hit a - to -',
            '- pitches to -',
            '- - on strikes',
            '- pitching for -',
            '- - -, - stole -',
            '- to - on - by -',
            '- - to -, - to -',
            '- - to - (- feet)',
            '- - to -, - scored',
            '- to - on - by - -',
            '- - to -, - - at -',
            '- reached on - to -',
            '- -, - to -, - to -',
            '- to - on - by - - -',
            '- -, - to - on - by -',
            '- -, - to -, - - at -',
            '- hit - to -, - scored',
            '- hit a - to -, - to -',
            '- safe at - on - by - -',
            '- - to -, - scored, - -',
            '- hit a - to -, - scored',
            '- to -, - to - on - by -',
            '- - to -, - to -, - to -',
            '- safe at - on - by - - -',
            '- - to -, - thrown - at -',
            '- - and caught stealing -',
            '- -, - to - to -, - - at -',
            '- - to -, - scored, - to -',
            '- - to -, - to -, - - at -',
            '- - to -, - - at -, - to -',
            '- scored on - -, - stole -',
            '- -, to -, - doubled off -',
            '- scored, - to - on - by -',
            '- reached on - to -, - to -',
            '- - to - (- feet), - scored',
            '- -, - to -, - doubled off -',
            '- -, - to -, - thrown - at -',
            '- - to -, - scored, - - at -',
            '- -, - to -, - to -, - - at -',
            '- - to -, - - stretching at -',
            '- -, - to -, - - at -, - to -',
            '- reached on - to -, - scored',
            '- -, - scored, - to -, - to -',
            '- hit - to -, - scored, - to -',
            '- - -, - safe at - on - by - -',
            '- scored on a -, - to - on a -',
            '- reached on - to -, - - - at -',
            '- - to -, - scored and - scored',
            '- -, - to -, - - at -, - - at -',
            '- - to -, - scored on - by - - -',
            '- safe at - on - by - - -, - to -',
            '- - to -, - to -, - thrown - at -',
            '- - to -, - safe at - on - by - -',
            '- -, - to - on - by - - -, - to -',
            '- -, - to - to -, - doubled off -',
            '- scored on - -, - to - on - by -',
            '- -, - to - to -, - - at -, - to -',
            '- - to -, - to -, - to -, - - at -',
            '- - -, - caught stealing -, - to -',
            '- to - on - by -, - to - on - by -',
            '- - to -, - scored, - to -, - to -',
            '- reached on - to -, - to -, - to -',
            '- - to -, - scored, - thrown - at -',
            '- - to -, - safe at - on - by - - -',
            '- -, - to - to -, - scored, - - at -',
            '- - to -, - scored, - - at -, - to -',
            '- reached on - to -, - scored, - to -',
            '- - to -, - - stretching at -, - to -',
            '- hit - to -, - scored, - to -, - to -',
            '- scored on -, - safe at - on - by - -',
            '- safe at - on - by - -, - to -, - to -',
            '- - to -, - scored, - - stretching at -',
            '- - to -, - to -, - to -, - - at - in -',
            '- - to -, - scored and - scored, - to -',
            '- scored on -, - safe at - on - by - - -',
            '- - to - (- feet), - scored and - scored',
            '- reached - base on -, - to - on - by - -',
            '- - to -, - to -, - to -, - thrown - at -',
            '- safe at - on - by - -, - safe at - on -',
            '- - to -, - scored, - scored and - scored',
            '- safe at - on - by - - -, - to -, - to -',
            '- -, - to - to -, - to -, - to -, - - at -',
            '- - to -, - scored, - - at -, - - at - on -',
            '- - to -, - safe at - on - by - - -, - to -',
            '- - to -, - to -, - safe at - on - by - - -',
            '- safe at - on - by - - -, - safe at - on -',
            '- reached on - to -, - scored on - by - - -',
            '- - to -, - scored, - to -, - thrown - at -',
            '- reached on - to -, - safe at - on - by - -',
            '- -, - to - to -, - scored, - - at -, - to -',
            '- - to -, - - at -, - safe at - on - by - - -',
            '- safe at first and advances to - on - by - -',
            '- - to -, - safe at - on - by - - -, - - at -',
            '- -, - to - to - to -, - thrown - at -, - to -',
            '- reached on - to -, - safe at - on - by - - -',
            '- scored, - safe at -, - safe at - on - by - -',
            '- - to -, - scored on - by - -, - safe at - on -',
            '- scored, - safe at -, - safe at - on - by - - -',
            '- - to - (- feet), - scored, - scored and - scored',
            '- - to -, - scored on -, - safe at - on - by - - -',
            '- - to -, - to -, - to -, - safe at - on - by - - -',
            '- reached on - to -, - scored on - by - - -, - to -',
            '- scored on - -, - to - on - by -, - to - on - by -',
            '- reached on - to -, - to -, - safe at - on - by - -',
            '- - to -, - safe at - on - by - - -, - safe at - on -',
            '- reached - base on -, - to - on - by - -, - to - on -',
            '- reached on - to -, - to -, - safe at - on - by - - -',
            '- reached on - to -, - to - on - by - -, - to -, - to -',
            '- reached on - to -, - and - scored on - by - -, - to -',
            '- - to -, - scored on - by - - and - scored on -, - to -',
            '- reached on - to -, - to -, - to -, - safe at - on - by - - -',
            '- - to -, - scored, - scored on - by - - - and - scored, - to -',
            '- reached on - to -, - scored on - by - -, - to -, - safe at - on -',
            '- reached on - to -, - scored on - by - - - and - scored on -, - to -',
            '- - to -, - scored on - and - scored, - - at -, - safe at - on - by - - -',
            '- reached on - to -, - scored and - scored on - by - -, - to -, - safe at - on -'
        ]

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

        return description

    def validate(self, description: str, entities: Dict[str, Any]) -> Tuple[bool, str]:
        template = re.sub(r'\. *$', '', description)
        template = re.sub(r'by ((first|second|third) baseman|(right|left|center) fielder)', 'by - -', template)
        template = re.sub(r'by (pitcher|catcher|shortstop)', 'by -', template)

        template = self.create_template(template, entities)

        template = re.sub(r' +', ' ', template).strip()

        return template in self.__templates, template
