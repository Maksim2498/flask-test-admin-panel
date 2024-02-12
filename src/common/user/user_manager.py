from typing            import Any

from common.io.dialog  import Dialog
from common.io.storage import Storage

from .user             import User


__all__ = ["UserManager"]


class UserManager:
    storage: Storage[User]
    dialog:  Dialog | None

    __users: dict[int, User]

    def __init__(
        self,
        storage:    Storage[User],
        dialog:     Dialog | None = None,
        load_users: bool          = True
    ):
        self.storage = storage
        self.dialog  = dialog

        if load_users:
            self.load_all_users()
        else:
            self.__users = {}

    def show_all_users(self) -> Any:
        dialog = self.get_dialog()
        users  = self.__users.values()

        return dialog.show_many(users)

    def show_user(self, user_id: int) -> Any:
        dialog = self.get_dialog()
        user   = self.get_user(user_id)

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
        old_user = self.__users.get(user.id)

        if old_user is None or user is not old_user:
            if self.exists_user_with_login(user.login):
                raise ValueError(f"User with login \"{user.login}\" already exists")

            self.storage.persist(user)
            self.__users[user.id] = user
        else:
            self.storage.persist(user)

    @property
    def user_count(self) -> int:
        return len(self.__users)

    def get_user(self, user_id: int) -> User | None:
        return self.__users.get(user_id)

    def get_all_users(self) -> list[User]:
        return list(self.__users.values())

    def delete_user(self, user_id: int) -> bool:
        try:
            self.__users.pop(user_id)
            self.storage.delete(user_id)
            return True
        except KeyError:
            return False

    def delete_all_users(self) -> int:
        count = self.user_count

        self.__users.clear()
        self.storage.delete_all()

        return count

    def load_user(self, user_id: int) -> User | None:
        user = self.storage.load(user_id)

        if user is None:
            return None

        self.__users[user.id] = user

        return user

    def load_all_users(self) -> list[User]:
        self.__users = { user.id: user for user in self.storage.load_all() }
        return self.get_all_users()

    def persist_user(self, user_id: int) -> bool:
        user = self.get_user(user_id)

        if user is None:
            return False

        self.storage.persist(user)

        return True

    def persist_all_users(self):
        for user in self.__users.values():
            self.storage.persist(user)

    def exists_user_with_login(self, user_login: str) -> bool:
        for user in self.__users.values():
            if user.login == user_login:
                return True

        return False

    def exists_user_with_id(self, user_id: int) -> bool:
        return user_id in self.__users

    def view(self, **kwargs: Dialog | Storage | None) -> "UserManager":
        storage = kwargs.get("storage", self.storage)

        if not isinstance(storage, Storage):
            raise ValueError("storage kwarg must be of Storage type")

        dialog = kwargs.get("dialog",  self.dialog)

        if dialog is not None and not isinstance(dialog, Dialog):
            raise ValueError("dialog kwarg must be of None of Dialog type")

        manager = UserManager(storage, dialog, load_users = False)

        manager.__users = self.__users

        return manager
