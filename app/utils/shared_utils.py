def serialize_list(data: list, schema):
    return [schema.model_validate(item) for item in data]