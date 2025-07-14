def serialize_list(data: list, schema, extra_fields_func = None):
    result = []
    for item in data:
        if extra_fields_func:
            extra_field = extra_fields_func(item)
        else:
            extra_field = {}
        validated = schema.model_validate(item, update=extra_field)
        result.append(validated)
    return result