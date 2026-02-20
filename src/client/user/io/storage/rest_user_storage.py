from collections.abc import Iterable
from typing import Any, Literal, TypedDict, cast, override

import requests

from client.error import BadStatusCodeError
from client.util import validate_json
from common.io.storage import Storage
from common.user import User
from common.user.user_json import user_from_dict

__all__ = ["RestUserStorage"]


class RestUserStorage(Storage[User]):
  __url: str

  def __init__(self, url: str = "http://localhost:8000/api"):
    self.__url = url

  @property
  def url(self) -> str:
    return self.__url

  @override
  def persist(self, obj: User) -> int:
    if obj.id < 0:
      self.__register(obj)
    else:
      self.__update(obj)

    return obj.id

  def __register(self, user: User):
    url = f"{self.url}/users"
    res = requests.post(url, json=user.toDict())

    if res.status_code != 200:
      try:
        json = res.json()
        error = json["error"]

        if isinstance(error, str):
          raise RuntimeError(error)
      except Exception:
        ...

      raise BadStatusCodeError(res.status_code)

    class ErrorSchema(TypedDict):
      error: str

    class SuccessSchema(TypedDict):
      id: int

    Schema = ErrorSchema | SuccessSchema

    json = res.json()
    json = cast(ErrorSchema | SuccessSchema, validate_json(json, cast(Any, Schema)))
    error = json.get("error")

    if error is not None:
      raise RuntimeError(error)

    user._id = json["id"]

  def __update(self, user: User):
    url = f"{self.url}/users/{user.id}"
    res = requests.patch(url, json=user.toDict())

    if res.status_code != 200:
      raise BadStatusCodeError(res.status_code)

    class Schema(TypedDict):
      error: str | None

    json = res.json()
    json = validate_json(json, Schema)
    error = json.get("error")

    if error is not None:
      raise RuntimeError(error)

  class __UserSchema(TypedDict):
    role: Literal["user"]
    id: int
    login: str
    name: str | None

  class __ModeratorSchema(TypedDict):
    role: Literal["moderator"]
    id: int
    login: str
    name: str | None
    verified_users: list[str]

  class __AdminSchema(TypedDict):
    role: Literal["admin"]
    id: int
    login: str
    name: str | None
    verified_users: list[str]
    created_pages: list[str]

  __AnyUserSchema = __UserSchema | __ModeratorSchema | __AdminSchema

  @override
  def load_all(self) -> Iterable[User]:
    res = requests.get(f"{self.url}/users")

    if res.status_code != 200:
      raise BadStatusCodeError(res.status_code)

    json = res.json()
    json = validate_json(json, list[RestUserStorage.__AnyUserSchema])

    return map(lambda row: user_from_dict(dict(row)), json)

  @override
  def load(self, user_id: int) -> User | None:
    res = requests.get(f"{self.url}/users/{user_id}")

    if res.status_code == 404:
      return None

    if res.status_code != 200:
      raise BadStatusCodeError(res.status_code)

    json = res.json()
    json = validate_json(json, cast(Any, RestUserStorage.__AnyUserSchema))

    return user_from_dict(dict(json))

  @override
  def load_all_ids(self) -> Iterable[int]:
    res = requests.get(f"{self.url}/users/ids")

    if res.status_code != 200:
      raise BadStatusCodeError(res.status_code)

    return validate_json(res.json(), list[int])

  @override
  def count(self) -> int:
    res = requests.get(f"{self.url}/users/count")

    if res.status_code != 200:
      raise BadStatusCodeError(res.status_code)

    return validate_json(res.json(), int)

  @override
  def delete(self, user_id: int) -> bool:
    res = requests.delete(f"{self.url}/users/{user_id}")

    if res.status_code == 404:
      return False

    if res.status_code != 200:
      raise BadStatusCodeError(res.status_code)

    class Schema(TypedDict):
      deleted: bool

    json = res.json()
    json = validate_json(json, Schema)

    return json["deleted"]

  @override
  def delete_all(self) -> int:
    res = requests.delete(f"{self.url}/users")

    if res.status_code != 200:
      raise BadStatusCodeError(res.status_code)

    class Schema(TypedDict):
      deleted: int

    json = res.json()
    json = validate_json(json, Schema)

    return json["deleted"]
