from typing import Any, Iterable, override

from .user  import User


__all__ = ["Moderator"]


class Moderator(User):
    role = "moderator"

    _verified_users: frozenset[str]

    def __init__(
        self,
        login:          str           = "moder",
        name:           str | None    = None,
        verified_users: Iterable[str] = [],
    ):
        super().__init__(login, name)

        self._verified_users = frozenset(verified_users)

    @override
    def toDict(self) -> dict[str, Any]:
        d = super().toDict()
        d["verified_users"] = list(self.verified_users)
        return d

    @property
    def verified_users(self) -> frozenset[str]:
        return self._verified_users

    @verified_users.setter
    def verified_users(self, new_verified_users: Iterable[str]):
        def normalize_and_check_login(login: str) -> str:
            login = User.normalize_login(login)
            User.check_normalized_login(login)
            return login

        self._verified_users = frozenset(map(normalize_and_check_login, new_verified_users))

    def __repr__(self) -> str:
        return (
            f"Moderator(login={repr(self.login)},\n" +
            f"          name={repr(self.name)},\n"   +
            f"          verified_users={repr(self.verified_users)})"
        )
