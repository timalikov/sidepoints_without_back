import re

def camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def serialize_profile_data(profile_data: dict) -> dict:
    serialized_data = {}
    for key, value in profile_data.items():
        new_key = camel_to_snake(key) if '_' not in key else key
        serialized_data[new_key] = value
    return serialized_data
