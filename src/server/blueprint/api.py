from typing import cast

from flask import Blueprint, Response, jsonify, request

from common.user import Admin, Moderator, User, UserManager
from server.io.dialog import JsonDialog
from server.multi_user_manager import MultiUserManager

__all__ = ["create_blueprint"]


def _get_manager(multi: MultiUserManager) -> tuple[UserManager | None, tuple[Response, int] | None]:
  storage = request.args.get("storage")
  if storage is not None and storage not in multi.enabled_storages:
    return None, (jsonify(error=f"Unknown or disabled storage: {storage}"), 400)
  manager = multi.get_manager_or_default(storage)
  if manager is None:
    return None, (jsonify(error="No storage backend enabled"), 503)
  return manager, None


def create_blueprint(multi_manager: MultiUserManager) -> Blueprint:
  blueprint = Blueprint("api", __name__)

  @blueprint.get("/users/ids")
  def get_all_user_ids():
    manager, err = _get_manager(multi_manager)
    if err is not None:
      return err[0], err[1]
    manager = manager.view(dialog=JsonDialog())
    users = manager.get_all_users()
    ids = [u.id for u in users]
    return jsonify(ids)

  @blueprint.get("/users/count")
  def get_user_count():
    manager, err = _get_manager(multi_manager)
    if err is not None:
      return err[0], err[1]
    return jsonify(manager.user_count)

  @blueprint.get("/users")
  def get_all_users():
    manager, err = _get_manager(multi_manager)
    if err is not None:
      return err[0], err[1]
    manager = manager.view(dialog=JsonDialog())
    return manager.show_all_users()

  @blueprint.get("/users/<int:id>")
  def get_user(id: int):
    manager, err = _get_manager(multi_manager)
    if err is not None:
      return err[0], err[1]
    manager = manager.view(dialog=JsonDialog())
    res = cast(Response, manager.show_user(id))
    res.status_code = 404 if res.json is None else 200
    return res

  @blueprint.post("/users")
  def register_user():
    manager, err = _get_manager(multi_manager)
    if err is not None:
      return err[0], err[1]
    manager = manager.view(dialog=JsonDialog())
    json = request.json

    if not isinstance(json, dict):
      return jsonify(error="Expected an object"), 400

    role = json.get("role")

    if role == User.role:
      user = User()
    elif role == Moderator.role:
      user = Moderator()
    elif role == Admin.role:
      user = Admin()
    else:
      return jsonify(error="Bad role"), 400

    try:
      manager.prompt_user(user)
    except ValueError as e:
      return jsonify(error=str(e)), 400

    return manager.get_dialog().show(user)

  @blueprint.patch("/users/<int:id>")
  def update_user(id: int):
    manager, err = _get_manager(multi_manager)
    if err is not None:
      return err[0], err[1]
    manager = manager.view(dialog=JsonDialog())
    user = manager.get_user(id)

    if user is None:
      return jsonify(error=f"User with id {id} not found"), 404

    try:
      manager.prompt_user(user)
    except ValueError as e:
      return jsonify(error=str(e)), 400

    return manager.get_dialog().show(user)

  @blueprint.delete("/users")
  def delete_all_users():
    manager, err = _get_manager(multi_manager)
    if err is not None:
      return err[0], err[1]
    return jsonify(deleted=manager.delete_all_users())

  @blueprint.delete("/users/<int:id>")
  def delete_user(id: int):
    manager, err = _get_manager(multi_manager)
    if err is not None:
      return err[0], err[1]
    deleted = manager.delete_user(id)
    code = 200 if deleted else 404
    return jsonify(deleted=deleted), code

  return blueprint
