from abc              import abstractmethod
from typing           import Any, Iterable, cast, override

from common.util.type import cast_text, get_attr_info

from .dialog          import Dialog


__all__ = ["TextDialog"]


class TextDialog(Dialog):
    @abstractmethod
    def get_attr_text(self, obj: Any, attr_name: str) -> str | None: ...

    @abstractmethod
    def show(self, obj: Any, **kwargs: Any) -> str: ...

    @override
    def show_many(self, objs: Iterable[Any], **kwargs: Any) -> str:
        return "\n".join(super().show_many(objs, **kwargs))

    @override
    def prompt_attr(self, obj: Any, attr_name: str):
        text = self.get_attr_text(obj, attr_name)

        if text is None:
            return

        attr_info = get_attr_info(obj, attr_name)
        attr_type = None if attr_info is None else attr_info.value_type

        if attr_type is None:
            setattr(obj, attr_name, text)
            return

        value = cast_text(text, cast(Any, attr_type))

        setattr(obj, attr_name, value)
