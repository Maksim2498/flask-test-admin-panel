from typing            import Any, Final, override

from common.io.storage import Identifiable
from common.util       import ToDictConvertible

import re


__all__ = ["User"]


class User(Identifiable, ToDictConvertible):
    @staticmethod
    def check_login(login: str):
        User.check_normalized_login(User.normalize_login(login))

    @staticmethod
    def check_normalized_login(login: str):
        MIN_LEN: Final = 4
        MAX_LEN: Final = 32

        if len(login) < MIN_LEN:
            raise ValueError(f"Login is too short (minimum {MIN_LEN} characters required)")

        if len(login) > MAX_LEN:
            raise ValueError(f"Login is too long (maximum {MAX_LEN} characters allowed)")

        if re.search("[^a-zA-Z0-9]", login):
            raise ValueError("Login must contain only english letters and digits")

    @staticmethod
    def normalize_login(login: str) -> str:
        return login.strip()

    @staticmethod
    def check_name(name: str | None):
        User.check_normalized_name(User.normalize_name(name))

    @staticmethod
    def check_normalized_name(name: str | None):
        if name is None:
            return

        MIN_LEN: Final = 4
        MAX_LEN: Final = 64

        if len(name) < MIN_LEN:
            raise ValueError(f"Name is too short (minimum {MIN_LEN} characters required)")

        if len(name) > MAX_LEN:
            raise ValueError(f"Name is too long (maximum {MAX_LEN} characters allowed)")

    @staticmethod
    def normalize_name(name: str | None) -> str | None:
        return None if name is None else re.sub("\\s+", " ", name.strip())

    role = "user"

    _login: str
    _name:  str | None

    def __init__(self, login: str = "user", name: str | None = None):
        super().__init__()

        self.login = login
        self.name  = name

    @override
    def toDict(self) -> dict[str, Any]:
        return {
            "role":  self.role,
            "id":    self.id,
            "login": self.login,
            "name":  self.name,
        }

    @property
    def login(self) -> str:
        return self._login

    @login.setter
    def login(self, new_login: str):
        new_login = User.normalize_login(new_login)
        User.check_normalized_login(new_login)
        self._login = new_login

    @property
    def name(self) -> str | None:
        return self._name

    @name.setter
    def name(self, new_name: str | None):
        new_name = User.normalize_name(new_name)
        User.check_normalized_name(new_name)
        self._name = new_name

    def __repr__(self) -> str:
        return (
            f"User(login={repr(self.login)},\n" +
            f"     name={repr(self.name)})"
        )
