import json


class ComplexEncoder(json.JSONEncoder):

    def default(self, o):
        if 'as_json' in dir(o) and callable(getattr(o, 'as_json')):
            return json.loads(o.as_json())
        return super().default(o)
