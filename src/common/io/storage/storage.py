from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Generic, TypeVar

from .identifiable import Identifiable

__all__ = ["Storage"]


T = TypeVar("T", bound=Identifiable)


class Storage(ABC, Generic[T]):
  @abstractmethod
  def persist(self, obj: T) -> int: ...

  @abstractmethod
  def load(self, obj_id: int) -> T | None: ...

  @abstractmethod
  def load_all_ids(self) -> Iterable[int]: ...

  @abstractmethod
  def delete(self, obj_id: int) -> bool: ...

  def count(self) -> int:
    return len(list(self.load_all_ids()))

  def load_all(self) -> Iterable[T]:
    for obj_id in self.load_all_ids():
      obj = self.load(obj_id)

      if obj is not None:
        yield obj

  def delete_all(self) -> int:
    deleted = 0

    for obj_id in self.load_all_ids():
      deleted += self.delete(obj_id)

    return deleted
