from common.user import UserManager

__all__ = ["MultiUserManager"]


class MultiUserManager:
  __managers: dict[str, UserManager]
  __enabled: list[str]

  def __init__(self, managers: dict[str, UserManager], enabled: list[str]):
    self.__managers = managers
    self.__enabled = list(enabled)

  @property
  def enabled_storages(self) -> list[str]:
    return list(self.__enabled)

  def get_manager(self, storage_name: str) -> UserManager | None:
    if storage_name not in self.__enabled:
      return None
    return self.__managers.get(storage_name)

  def get_manager_or_default(self, storage_name: str | None) -> UserManager | None:
    if storage_name is not None:
      manager = self.get_manager(storage_name)
      if manager is not None:
        return manager
    return self.__managers.get(self.__enabled[0]) if self.__enabled else None

  def persist_all_users(self):
    for manager in self.__managers.values():
      manager.persist_all_users()
