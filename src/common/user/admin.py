from typing     import Any, Iterable, override

from .moderator import Moderator


__all__ = ["Admin"]


class Admin(Moderator):
    role = "admin"

    _created_pages: frozenset[str]

    def __init__(
        self,
        login:          str           = "admin",
        name:           str | None    = None,
        verified_users: Iterable[str] = [],
        created_pages:  Iterable[str] = [],
    ):
        super().__init__(login, name, verified_users)

        self._created_pages = frozenset(created_pages)

    @override
    def toDict(self) -> dict[str, Any]:
        d = super().toDict()
        d["created_pages"] = list(self.created_pages)
        return d

    @property
    def created_pages(self) -> frozenset[str]:
        return self._created_pages

    @created_pages.setter
    def created_pages(self, new_created_pages: Iterable[str]):
        self._created_pages = frozenset(
            filter(
                lambda p: len(p) > 0,
                map(str.strip, new_created_pages)
            )
        )

    def __repr__(self) -> str:
        return (
            f"Admin(login={repr(self.login)},\n"                   +
            f"      name={repr(self.name)},\n"                     +
            f"      verified_users={repr(self.verified_users)},\n" +
            f"      created_pages={repr(self.created_pages)})"
        )
