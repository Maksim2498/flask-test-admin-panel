"""JSON RPC request dispatch for user storage (worker side)."""

from typing import Any

from common.io.storage import Storage
from common.user import User
from common.user.user_json import user_from_dict, user_to_dict

__all__ = ["dispatch_storage_rpc"]


def dispatch_storage_rpc(storage: Storage[User], request: dict[str, Any]) -> Any:
  method = request["method"]
  args = request.get("args") or {}

  match method:
    case "load":
      uid = int(args["id"])
      user = storage.load(uid)
      return None if user is None else user_to_dict(user)
    case "persist":
      user = user_from_dict(args["user"])
      return storage.persist(user)
    case "delete":
      return storage.delete(int(args["id"]))
    case "count":
      return storage.count()
    case "load_all_ids":
      return list(storage.load_all_ids())
    case "load_all":
      return [user_to_dict(u) for u in storage.load_all()]
    case "delete_all":
      return storage.delete_all()
    case _:
      raise ValueError(f"Unknown RPC method: {method}")
