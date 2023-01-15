import json


class ComplexEncoder(json.JSONEncoder):

    def default(self, o):
        if 'for_json' in dir(o) and callable(getattr(o, 'for_json')):
            return o.for_json()
        if 'as_json' in dir(o) and callable(getattr(o, 'as_json')):
            return json.loads(o.as_json())
        return o.__dir__
