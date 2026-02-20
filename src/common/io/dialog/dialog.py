from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any

from common.util.type import get_all_typed_attrs_info

__all__ = ["Dialog"]


class Dialog(ABC):
  @abstractmethod
  def prompt_attr(self, obj: Any, attr_name: str): ...

  @abstractmethod
  def show(self, obj: Any, **kwargs: Any) -> Any: ...

  def prompt_all_attrs(self, obj: Any):
    for attr in get_all_typed_attrs_info(obj).values():
      if not attr.readonly:
        self.prompt_attr(obj, attr.name)

  def show_many(self, objs: Iterable[Any], **kwargs: Any) -> Any:
    return [self.show(obj, **kwargs) for obj in objs]
