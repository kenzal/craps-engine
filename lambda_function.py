import json
import engine
from JsonEncoder import ComplexEncoder


def lambda_handler(event, context):
    result = engine.process_request(event)
    if not isinstance(result, str):
        result = json.dumps(result, cls=ComplexEncoder)
    return json.loads(result)
