from abc import ABC, abstractmethod
from typing import Any

__all__ = ["ToDictConvertible"]


class ToDictConvertible(ABC):
  @abstractmethod
  def toDict(self) -> dict[str, Any]: ...
