from collections.abc import Iterable
from typing import cast, override

from pymongo import MongoClient
from pymongo.collection import Collection

from common.io.storage import Storage
from common.user import Admin, Moderator, User

__all__ = ["MongoUserStorage"]


def _doc_to_user(doc: dict) -> User:
  user_id = doc["id"]
  login = doc["login"]
  name = doc.get("name")
  role = doc.get("role", "user")

  user: User

  if role == "admin":
    user = Admin()
    user._verified_users = frozenset(doc.get("verified_users", []))
    user._created_pages = frozenset(doc.get("created_pages", []))
  elif role == "moderator":
    user = Moderator()
    user._verified_users = frozenset(doc.get("verified_users", []))
  else:
    user = User()

  user._id = user_id
  user._login = login
  user._name = name

  return user


def _user_to_doc(user: User) -> dict:
  doc: dict = {
    "id": user.id,
    "login": user.login,
    "name": user.name,
    "role": user.role,
  }
  if isinstance(user, Moderator):
    doc["verified_users"] = list(user.verified_users)
  if isinstance(user, Admin):
    doc["created_pages"] = list(user.created_pages)
  return doc


def _build_mongo_uri(host: str, port: int, database: str, user: str | None, password: str | None) -> str:
  if user and password:
    return f"mongodb://{user}:{password}@{host}:{port}/{database}"
  return f"mongodb://{host}:{port}/{database}"


class MongoUserStorage(Storage[User]):
  __collection: Collection

  def __init__(
    self,
    host: str,
    port: int = 27017,
    database: str = "admin_panel",
    collection: str = "users",
    user: str | None = None,
    password: str | None = None,
  ):
    super().__init__()
    uri = _build_mongo_uri(host, port, database, user, password)
    client = MongoClient(uri)
    db = client[database]
    self.__collection = db[collection]
    self.__collection.create_index("id", unique=True)

  @override
  def persist(self, obj: User) -> int:
    return self.__insert(obj) if obj.id < 0 else self.__update(obj)

  def __next_id(self) -> int:
    result = self.__collection.find_one(sort=[("id", -1)], projection={"id": 1})
    return (result["id"] + 1) if result else 1

  def __insert(self, user: User) -> int:
    user._id = self.__next_id()
    doc = _user_to_doc(user)
    self.__collection.insert_one(doc)
    return user.id

  def __update(self, user: User) -> int:
    doc = _user_to_doc(user)
    result = self.__collection.replace_one({"id": user.id}, doc)
    if result.matched_count == 0:
      raise ValueError(f"User with id {user.id} not found")
    return user.id

  @override
  def load(self, user_id: int) -> User | None:
    doc = self.__collection.find_one({"id": user_id})
    if doc is None:
      return None
    return _doc_to_user(doc)

  @override
  def load_all_ids(self) -> Iterable[int]:
    cursor = self.__collection.find(projection={"id": 1})
    return (doc["id"] for doc in cursor)

  @override
  def count(self) -> int:
    return cast(int, self.__collection.count_documents({}))

  @override
  def delete(self, user_id: int) -> bool:
    result = self.__collection.delete_one({"id": user_id})
    return result.deleted_count > 0

  @override
  def delete_all(self):
    self.__collection.delete_many({})
