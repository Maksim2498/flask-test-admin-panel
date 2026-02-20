from abc import ABC

__all__ = ["Identifiable"]


class Identifiable(ABC):
  _id: int

  def __init__(self, id: int = -1):
    self._id = id

  @property
  def id(self) -> int:
    return self._id
