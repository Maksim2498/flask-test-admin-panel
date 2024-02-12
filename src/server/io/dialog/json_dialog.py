from typing           import Any, Iterable

from flask            import Response, jsonify, request

from common.io.dialog import Dialog
from common.util.type import get_attr_info, is_of_type
from common.util      import ToDictConvertible


__all__ = ["JsonDialog"]


class JsonDialog(Dialog):
    def prompt_attr(self, obj: Any, attr_name: str):
        json = request.json

        if json is None or not isinstance(json, dict):
            return

        value = json.get(attr_name)

        if value is None:
            return

        attr_info = get_attr_info(obj, attr_name)

        if attr_info is None:
            setattr(obj, attr_name, value)
            return

        if not is_of_type(value, attr_info.value_set_type):
            raise ValueError(f"Attribute {repr(attr_name)} is of invalid type")

        setattr(obj, attr_name, value)

    def show_many(self, objs: Iterable[Any], **kwargs: Any) -> Response:
        return jsonify([
            obj.toDict() if isinstance(obj, ToDictConvertible) else obj
            for obj in objs
        ])

    def show(self, obj: Any, **kwargs: Any) -> Response:
        if isinstance(obj, ToDictConvertible):
            obj = obj.toDict()

        return jsonify(obj)
