import json


def query_builder(query, operation_name=None, variables=None, input_data=None):
    data = dict(
        query=query, operation_name=operation_name
    )
    if variables:
        data["variables"] = variables
    if input_data:
        if variables in data:
            data["variables"]["input"] = input_data
        else:
            data["variables"] = {"input": input_data}
    return json.dumps(data)
