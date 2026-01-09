from __future__ import annotations
from jsonschema import Draft202012Validator, Draft7Validator, validate as js_validate
from jsonschema.exceptions import ValidationError
import json
from pathlib import Path

# We try draft2020-12, fallback to draft7

def _get_validator(schema: dict):
    if "$schema" in schema and "2020-12" in schema["$schema"]:
        return Draft202012Validator(schema)
    return Draft7Validator(schema)

class SchemaValidator:
    def __init__(self):
        pass

    def validate(self, instance_path: Path, schema_path: Path) -> tuple[bool, str | None]:
        with open(schema_path, 'r', encoding='utf-8') as sf:
            schema = json.load(sf)
        with open(instance_path, 'r', encoding='utf-8') as inf:
            instance = json.load(inf)
        try:
            _get_validator(schema).validate(instance)
            return True, None
        except ValidationError as e:
            return False, str(e)
