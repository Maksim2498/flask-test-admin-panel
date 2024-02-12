from typing       import Any, TypeVar, Union, Literal, cast, get_args, get_origin, get_type_hints
from types        import NoneType, UnionType

from client.error import BadJsonSchemaError


__all__ = ["validate_json"]


T = TypeVar("T")

def validate_json(json: Any, schema: type[T]) -> T:
    if schema is None:
        schema = NoneType

    # Non-Generics

    for nongeneric_type in [NoneType, bool, int, float, str, list, set, frozenset]:
        if schema is nongeneric_type:
            if not isinstance(json, nongeneric_type):
                raise BadJsonSchemaError()

            return cast(T, json)

    origin = get_origin(schema)

    # Union

    if origin is UnionType or origin is Union:
        for type_variant in get_args(schema):
            try:
                return validate_json(json, type_variant)
            except:
                ...
        
        raise BadJsonSchemaError()

    # Literal

    if origin is Literal:
        literals = get_args(schema)

        if json not in literals:
            raise BadJsonSchemaError()

        return cast(T, json)

    # Collections

    for collection_type in [list, set, frozenset]:
        if origin is collection_type:
            if not isinstance(json, collection_type):
                raise BadJsonSchemaError()

            item_type = get_args(schema)[0]
            
            for item in json:
                validate_json(item, item_type)

        return cast(T, json)

    # Dict

    if origin is dict:
        if not isinstance(json, dict):
            raise BadJsonSchemaError()

        key_type, value_type = get_args(schema)

        for key, value in json.items():
            validate_json(key,   key_type  )
            validate_json(value, value_type)

        return cast(T, json)

    # Tuple

    if origin is tuple:
        if not isinstance(json, tuple) and not isinstance(json, list):
            raise BadJsonSchemaError()

        item_types = get_args(schema)

        if len(item_types) != len(json):
            raise BadJsonSchemaError()

        for item, item_type in zip(json, item_types):
            validate_json(item, item_type)

        return cast(T, json)

    # TypedDict

    if not issubclass(schema, dict):
        raise ValueError("Bad schema value")

    if not isinstance(json, dict):
        raise BadJsonSchemaError()

    hints = get_type_hints(schema)

    for item_name, item_type in hints.items():
        item = json.get(item_name)

        validate_json(item, item_type)

    return cast(T, json)
