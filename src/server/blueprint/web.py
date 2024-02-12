from flask             import Blueprint, render_template, redirect, url_for, request, flash

from common.user       import UserManager, Admin, Moderator, User
from server.io.dialog  import WebDialog
from server.util.flask import render_object


__all__ = ["create_blueprint"]


def create_blueprint(user_manager: UserManager) -> Blueprint:
    user_manager = user_manager.view(dialog = WebDialog())
    blueprint    = Blueprint("web", __name__)

    @blueprint.get("/")
    def index():
        return render_template(
            "index.jinja",
            users  = user_manager.get_all_users(),
            render = render_object,
        )

    @blueprint.route("/register/admin", methods = ["GET", "POST"])
    def register_admin():
        return register(Admin())

    @blueprint.route("/register/moderator", methods = ["GET", "POST"])
    def register_moderator():
        return register(Moderator())

    @blueprint.route("/register/user", methods = ["GET", "POST"])
    def register_user():
        return register(User())

    def register(user: User):
        if request.method == "POST":
            try:
                user_manager.prompt_user(user)
                return redirect(url_for(".index"))
            except Exception as e:
                flash(str(e), "error")

        return user_manager.get_dialog().show(
            user,
            title       = f"{user.__class__.__name__} Registration",
            submit_text = "Register",
        )

    @blueprint.route("/users/<int:id>", methods = ["GET", "POST"])
    def edit_user(id: int):
        user = user_manager.get_user(id)

        if user is None:
            return render_template("user-404.jinja"), 404

        if request.method == "POST":
            try:
                user_manager.prompt_user(user)
                return redirect(url_for(".index"))
            except Exception as e:
                flash(str(e), "error")

        return user_manager.get_dialog().show(
            user,
            title       = f"Edit {user.__class__.__name__}",
            submit_text = "Edit",
        )

    @blueprint.delete("/users/<int:id>")
    def delete_user(id: int):
        return "", 204 if user_manager.delete_user(id) else 404

    @blueprint.delete("/users/")
    def delete_all_users():
        user_manager.delete_all_users()
        return "", 204

    @blueprint.teardown_app_request
    def tear_down(exception):
        user_manager.persist_all_users()

    @blueprint.get("/<path:subpath>")
    def page_not_found(subpath):
        return render_template("404.jinja"), 404

    return blueprint
