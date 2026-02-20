"""Serialize / deserialize User (and subclasses) for JSON-based transports (REST, RabbitMQ RPC)."""

from typing import Any, Literal, TypedDict, cast

from .admin import Admin
from .moderator import Moderator
from .user import User

__all__ = ["user_from_dict", "user_to_dict"]


def user_to_dict(user: User) -> dict[str, Any]:
  return user.toDict()


class _UserSchema(TypedDict):
  role: Literal["user"]
  id: int
  login: str
  name: str | None


class _ModeratorSchema(TypedDict):
  role: Literal["moderator"]
  id: int
  login: str
  name: str | None
  verified_users: list[str]


class _AdminSchema(TypedDict):
  role: Literal["admin"]
  id: int
  login: str
  name: str | None
  verified_users: list[str]
  created_pages: list[str]


_AnyUserSchema = _UserSchema | _ModeratorSchema | _AdminSchema


def user_from_dict(data: dict[str, Any]) -> User:
  json = cast(_AnyUserSchema, data)
  role = json["role"]

  if role == "user":
    user = User()
  elif role == "moderator":
    user = Moderator()
  elif role == "admin":
    user = Admin()
  else:
    raise ValueError(f"Bad role: {repr(role)}")

  user._id = json["id"]
  user.login = json["login"]
  user.name = json["name"]

  if isinstance(user, Moderator):
    user.verified_users = cast(Any, json)["verified_users"]

  if isinstance(user, Admin):
    user.created_pages = cast(Any, json)["created_pages"]

  return user
