from typing import cast

from flask import Blueprint, Response, jsonify, request

from common.user import Admin, Moderator, User, UserManager
from server.io.dialog import JsonDialog

__all__ = ["create_blueprint"]


def create_blueprint(user_manager: UserManager) -> Blueprint:
  user_manager = user_manager.view(dialog=JsonDialog())
  blueprint = Blueprint("api", __name__)

  @blueprint.get("/users/ids")
  def get_all_user_ids():
    users = user_manager.get_all_users()
    ids = list(map(lambda user: user.id, users))

    return jsonify(ids)

  @blueprint.get("/users/count")
  def get_user_count():
    return jsonify(user_manager.user_count)

  @blueprint.get("/users")
  def get_all_users():
    return user_manager.show_all_users()

  @blueprint.get("/users/<int:id>")
  def get_user(id: int):
    res = cast(Response, user_manager.show_user(id))
    res.status_code = 404 if res.json is None else 200

    return res

  @blueprint.post("/users")
  def register_user():
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
      user_manager.prompt_user(user)
    except ValueError as e:
      return jsonify(error=str(e)), 400

    return user_manager.get_dialog().show(user)

  @blueprint.patch("/users/<int:id>")
  def update_user(id: int):
    user = user_manager.get_user(id)

    if user is None:
      return jsonify(error=f"User with id {id} not found"), 404

    try:
      user_manager.prompt_user(user)
    except ValueError as e:
      return jsonify(error=str(e)), 400

    return user_manager.get_dialog().show(user)

  @blueprint.delete("/users")
  def delete_all_users():
    return jsonify(deleted=user_manager.delete_all_users())

  @blueprint.delete("/users/<int:id>")
  def delete_user(id: int):
    deleted = user_manager.delete_user(id)
    code = 200 if deleted else 404

    return jsonify(deleted=deleted), code

  return blueprint
