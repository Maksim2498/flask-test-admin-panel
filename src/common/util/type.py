from dataclasses     import dataclass
from collections.abc import Iterable
from typing          import Any, Union, TypeVar, cast, get_origin, get_args, get_type_hints
from types           import UnionType, NoneType

import re


__all__ = [
    "AttrInfo",

    "get_all_typed_attrs_info",
    "get_attr_info",

    "cast_text",
    "is_of_type",
    "is_iterable",
]


@dataclass
class AttrInfo:
    name:           str
    value:          Any  = None
    readonly:       bool = False
    value_type:     type = cast(Any, None)
    value_set_type: type = cast(Any, None)

    def __post_init__(self):
        value_type = type(self.value)

        if self.value_type is None:
            self.value_type = value_type

        if self.value_set_type is None:
            self.value_set_type = self.value_type

    @property
    def placeholder(self) -> str:
        return AttrInfo.__placeholder(self.value_type)

    @staticmethod
    def __placeholder(value_type: type, plural: bool = False) -> str:
        origin = get_origin(value_type)

        return (
            AttrInfo.__non_generic_placeholder(value_type, plural)
            if origin is None else
            AttrInfo.__generic_placeholder(value_type, plural)
        )

    @staticmethod
    def __non_generic_placeholder(value_type: type, plural: bool = False) -> str:
        if value_type is str:
            placeholder = "string"
        elif value_type is int:
            placeholder = "integer"
        elif value_type is float:
            placeholder = "real"
        elif value_type is NoneType:
            placeholder = "blank"
        else:
            placeholder = "value"

        if plural:
            placeholder += "s"

        return placeholder

    @staticmethod
    def __generic_placeholder(value_type: type, plural: bool = False) -> str:
        origin = get_origin(value_type)

        assert origin is not None

        if origin is UnionType or origin is Union:
            args             = get_args(value_type)
            placeholded_args = map(lambda arg: AttrInfo.__placeholder(arg, plural), args)

            placeholder = " or ".join(placeholded_args)
        elif origin in [list, set, frozenset]:
            arg = get_args(value_type)[0]

            placeholder = f"comma-separated {AttrInfo.__placeholder(arg, True)}"
        else:
            placeholder = "value"

        if plural:
            placeholder += "s"

        return placeholder

    @property
    def zero(self) -> bool:
        if self.value is None:
            return True

        if isinstance(self.value, list) and len(self.value) == 0:
            return True
        
        return False

    @property
    def display_name(self) -> str:
        display_name = self.name

        while display_name.startswith("_"):
            display_name = display_name[1:]

        display_name = display_name.replace("_", " ")
        display_name = display_name.capitalize()
            
        return display_name

    @property
    def display_value(self) -> str:
        if self.value is None:
            return "none"

        for collection_type in [list, set, frozenset]:
            if isinstance(self.value, collection_type):
                return "empty" if len(self.value) == 0 else ", ".join(self.value)

        return str(self.value)

    @property
    def text_value(self) -> str:
        if self.value is None:
            return ""

        for collection_type in [list, set, frozenset]:
            if isinstance(self.value, collection_type):
                return ", ".join(self.value)

        return str(self.value)

    def __repr__(self) -> str:
        return (
            f"AttrInfo(name={repr(self.name)},\n"         +
            f"         value={repr(self.value)},\n"       +
            f"         readonly={repr(self.readonly)},\n" +
            f"         value_type={repr(self.value_type)})"
        )


def get_all_typed_attrs_info(obj: Any) -> dict[str, AttrInfo]:
    type_hints     = get_type_hints(type(obj))
    all_attrs_info = dict[str, AttrInfo]()

    for name in type_hints.keys():
        while name.startswith("_"):
            name = name[1:]

        attr_info = get_attr_info(obj, name, type_hints)

        if attr_info is None:
            continue

        all_attrs_info[name] = attr_info

    return all_attrs_info

def get_attr_info(
    obj:        Any,
    name:       str,
    type_hints: dict[str, Any] | None = None,
) -> AttrInfo | None:
    if not hasattr(obj, name) or name.startswith("_"):
        return None

    obj_type = type(obj)

    if type_hints is None:
        type_hints = get_type_hints(obj_type)

    value      = getattr(obj, name)
    value_type = type_hints.get(name)

    if value_type is None:
        value_type = type_hints.get("_" + name, type(value))

    attr = getattr(obj_type, name, None)

    if isinstance(attr, property):
        value_type = get_type_hints(attr.fget).get("return", value_type) if attr.fget is not None else value_type

        if attr.fset is None:
            value_set_type = value_type
            readonly       = True
        else:
            setter_type_hints = get_type_hints(attr.fset)

            if len(setter_type_hints) > 0:
                setter_arg_name = next(iter(setter_type_hints))
                value_set_type  = setter_type_hints[setter_arg_name]
            else:
                value_set_type = value_type

            readonly = False

        readonly  = attr.fset is None
    else:
        value_set_type = value_type
        readonly       = False

    return AttrInfo(
        name           = name,
        value          = value,
        value_type     = value_type,
        value_set_type = value_set_type,
        readonly       = readonly,
    )

T = TypeVar("T")

def cast_text(text: str, target_type: type[T]) -> T:
    origin = get_origin(target_type)

    return (
        _cast_text_to_non_generic(text, target_type)
        if origin is None else
        _cast_text_to_generic(text, target_type)
    )

def _cast_text_to_non_generic(text: str, target_type: Any) -> Any:
    if target_type is str:
        return text

    for scalar_type in [bool, int, float]:
        if target_type is scalar_type:
            return scalar_type(text)

    for collection_type in [list, set, frozenset]:
        if target_type is collection_type:
            splits          = re.split("\\s*,\\s*", text.strip())
            nonblank_splits = filter(bool, splits)

            return collection_type(nonblank_splits)

    raise NotImplementedError()

def _cast_text_to_generic(text: str, target_type: Any) -> Any:
    origin = get_origin(target_type)

    if origin is UnionType or origin is Union:
        args = get_args(target_type)

        if NoneType in args and len(text.strip()) == 0:
            return None

        for arg in args:
            try:
                return cast_text(text, arg)
            except:
                ...

        raise ValueError()

    for collection_type in [list, set, frozenset]:
        if origin is collection_type:
            splits          = re.split("\\s*,\\s*", text.strip())
            nonblank_splits = filter(bool, splits)
            arg             = get_args(target_type)[0]
            
            return [cast_text(split, arg) for split in nonblank_splits]

    raise NotImplementedError()

def is_of_type(obj: Any, test_type: type) -> bool:
    obj_type = type(obj)

    if obj_type == test_type:
        return True

    origin_type = get_origin(test_type)

    if origin_type is None:
        return False

    if origin_type is UnionType or origin_type is Union:
        type_args = get_args(test_type)

        return any(
            map(
                lambda arg: is_of_type(obj, arg),
                type_args,
            ),
        )

    for collection_type in [list, set, frozenset]:
        if origin_type is collection_type:
            if obj_type != collection_type:
                return False

            type_arg = get_args(test_type)[0]

            return all(
                map(
                    lambda item: is_of_type(item, type_arg),
                    obj,
                ),
            )

    if origin_type is Iterable:
        if not is_iterable(obj):
            return False

        type_args = get_args(test_type)

        if len(type_args) == 0:
            return True

        type_arg = type_args[0]

        return all(
            map(
                lambda item: is_of_type(item, type_arg),
                obj,
            ),
        )

    return False

def is_iterable(obj: Any) -> bool:
    try:
        iter(obj)
        return True
    except TypeError:
        return False
