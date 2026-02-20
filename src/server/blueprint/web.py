from flask import Blueprint, flash, redirect, render_template, request, url_for

from common.user import Admin, Moderator, User, UserManager
from server.io.dialog import WebDialog
from server.multi_user_manager import MultiUserManager
from server.util.flask import render_object

__all__ = ["create_blueprint"]


def _get_storage_and_manager(multi: MultiUserManager) -> tuple[str | None, UserManager | None]:
  storage = request.args.get("storage") or request.form.get("storage")
  manager = multi.get_manager_or_default(storage)
  current = (
    storage if storage in multi.enabled_storages else (multi.enabled_storages[0] if multi.enabled_storages else None)
  )
  return current, manager


def create_blueprint(multi_manager: MultiUserManager) -> Blueprint:
  blueprint = Blueprint("web", __name__)

  @blueprint.get("/")
  def index():
    current_storage, manager = _get_storage_and_manager(multi_manager)
    if manager is None:
      return "No storage backend enabled", 503
    manager = manager.view(dialog=WebDialog())
    return render_template(
      "index.jinja",
      users=manager.get_all_users(),
      render=render_object,
      enabled_storages=multi_manager.enabled_storages,
      current_storage=current_storage,
    )

  @blueprint.route("/register/admin", methods=["GET", "POST"])
  def register_admin():
    return register(Admin())

  @blueprint.route("/register/moderator", methods=["GET", "POST"])
  def register_moderator():
    return register(Moderator())

  @blueprint.route("/register/user", methods=["GET", "POST"])
  def register_user():
    return register(User())

  def register(user: User):
    current_storage, manager = _get_storage_and_manager(multi_manager)
    if manager is None:
      return "No storage backend enabled", 503
    manager = manager.view(dialog=WebDialog())
    if request.method == "POST":
      try:
        manager.prompt_user(user)
        return redirect(url_for(".index", storage=current_storage))
      except Exception as e:
        flash(str(e), "error")

    return manager.get_dialog().show(
      user,
      title=f"{user.__class__.__name__} Registration",
      submit_text="Register",
      storage=current_storage,
      enabled_storages=multi_manager.enabled_storages,
    )

  @blueprint.route("/users/<int:id>", methods=["GET", "POST"])
  def edit_user(id: int):
    current_storage, manager = _get_storage_and_manager(multi_manager)
    if manager is None:
      return "No storage backend enabled", 503
    manager = manager.view(dialog=WebDialog())
    user = manager.get_user(id)

    if user is None:
      return render_template("user-404.jinja"), 404

    if request.method == "POST":
      try:
        manager.prompt_user(user)
        return redirect(url_for(".index", storage=current_storage))
      except Exception as e:
        flash(str(e), "error")

    return manager.get_dialog().show(
      user,
      title=f"Edit {user.__class__.__name__}",
      submit_text="Edit",
      storage=current_storage,
      enabled_storages=multi_manager.enabled_storages,
    )

  @blueprint.delete("/users/<int:id>")
  def delete_user(id: int):
    _, manager = _get_storage_and_manager(multi_manager)
    if manager is None:
      return "", 503
    return "", 204 if manager.delete_user(id) else 404

  @blueprint.delete("/users/")
  def delete_all_users():
    _, manager = _get_storage_and_manager(multi_manager)
    if manager is None:
      return "", 503
    manager.delete_all_users()
    return "", 204

  @blueprint.teardown_app_request
  def tear_down(exception):
    multi_manager.persist_all_users()

  @blueprint.get("/<path:subpath>")
  def page_not_found(subpath):
    return render_template("404.jinja"), 404

  return blueprint
