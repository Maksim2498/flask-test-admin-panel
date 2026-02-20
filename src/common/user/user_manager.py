from typing import Any

from common.io.dialog import Dialog
from common.io.storage import Storage

from .user import User

__all__ = ["UserManager"]


class UserManager:
  storage: Storage[User]
  dialog: Dialog | None

  def __init__(self, storage: Storage[User], dialog: Dialog | None = None):
    self.storage = storage
    self.dialog = dialog

  def show_all_users(self) -> Any:
    dialog = self.get_dialog()
    users = list(self.storage.load_all())
    return dialog.show_many(users)

  def show_user(self, user_id: int) -> Any:
    dialog = self.get_dialog()
    user = self.get_user(user_id)
    return dialog.show(user)

  def prompt_user(self, user: User):
    dialog = self.get_dialog()
    dialog.prompt_all_attrs(user)
    self.add_user(user)

  def get_dialog(self) -> Dialog:
    if self.dialog is None:
      raise RuntimeError("dialog is None")
    return self.dialog

  def add_user(self, user: User):
    if user.id < 0:
      if self._exists_user_with_login(user.login):
        raise ValueError(f'User with login "{user.login}" already exists')
    else:
      if self._exists_user_with_login(user.login, exclude_id=user.id):
        raise ValueError(f'User with login "{user.login}" already exists')
    self.storage.persist(user)

  @property
  def user_count(self) -> int:
    return self.storage.count()

  def get_user(self, user_id: int) -> User | None:
    return self.storage.load(user_id)

  def get_all_users(self) -> list[User]:
    return list(self.storage.load_all())

  def delete_user(self, user_id: int) -> bool:
    return self.storage.delete(user_id)

  def delete_all_users(self) -> int:
    count = self.storage.count()
    self.storage.delete_all()
    return count

  def persist_all_users(self):
    pass

  def _exists_user_with_login(self, user_login: str, exclude_id: int | None = None) -> bool:
    for user in self.storage.load_all():
      if user.id != exclude_id and user.login == user_login:
        return True
    return False

  def exists_user_with_id(self, user_id: int) -> bool:
    return self.storage.load(user_id) is not None

  def view(self, **kwargs: Dialog | Storage | None) -> "UserManager":
    storage = kwargs.get("storage", self.storage)
    if not isinstance(storage, Storage):
      raise ValueError("storage kwarg must be of Storage type")

    dialog = kwargs.get("dialog", self.dialog)
    if dialog is not None and not isinstance(dialog, Dialog):
      raise ValueError("dialog kwarg must be of None of Dialog type")

    return UserManager(storage, dialog)
