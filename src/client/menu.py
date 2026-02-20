from collections.abc import Callable

from common.io.dialog import Dialog
from common.io.storage import Storage
from common.user import Admin, Moderator, User

from .util.cli import prompt_int_or_none, prompt_ranged_int_or_none

__all__ = ["Menu"]


class Menu:
  dialog: Dialog
  storage: Storage[User]

  __actions: list[tuple[str, Callable[[], None]]]

  def __init__(self, dialog: Dialog, storage: Storage[User]):
    self.dialog = dialog
    self.storage = storage
    self.__actions = [
      ("Show all users", self.__show_all_users),
      ("Show user", self.__show_user),
      ("Add new user", self.__add_user),
      ("Edit user", self.__edit_user),
      ("Remove user", self.__delete_user),
      ("Remove all users", self.__delete_all_users),
    ]

  def run(self):
    try:
      while True:
        self.__print_action_list()

        print()

        choice = self.__prompt_action_number()

        print()

        if choice is None:
          break

        _, action = self.__actions[choice - 1]

        try:
          action()
        except Exception as e:
          print(f"Failed to perform an action: {e}")

        print()
    except KeyboardInterrupt:
      print()

    print("\nBye!")

  def __print_action_list(self):
    print("Available actions:")

    print()

    for i, (action_name, _) in enumerate(self.__actions, 1):
      print(f"{i}: {action_name}")

  def __prompt_action_number(self) -> int | None:
    return prompt_ranged_int_or_none(
      "Enter number of action to perform (or nothing to quit): ",
      1,
      len(self.__actions),
    )

  def __show_all_users(self):
    for i, user in enumerate(self.storage.load_all()):
      if i > 0:
        print()

      self.dialog.show(user)

  def __show_user(self):
    user_id = Menu.__prompt_user_id_or_none()

    if user_id is None:
      return

    user = self.storage.load(user_id)

    if user is None:
      print(Menu.__make_user_with_id_not_found_message(user_id))
      return

    print()
    self.dialog.show(user)

  def __add_user(self):
    print("Who do you want to add?")
    print()
    print("1: User")
    print("2: Moderator")
    print("3: Admin")
    print()

    choice = prompt_ranged_int_or_none("Enter number of user type (or nothing to cancel): ", 1, 3)

    match choice:
      case 1:
        user = User()
      case 2:
        user = Moderator()
      case 3:
        user = Admin()
      case _:
        raise ValueError("Invalid user type id")

    print()
    self.dialog.prompt_all_attrs(user)
    self.storage.persist(user)
    print()
    print("User is successfully added")

  def __edit_user(self):
    user_id = Menu.__prompt_user_id_or_none()

    if user_id is None:
      return

    user = self.storage.load(user_id)

    if user is None:
      print(Menu.__make_user_with_id_not_found_message(user_id))
      return

    self.dialog.prompt_all_attrs(user)
    self.storage.persist(user)

    print("User is successfully edited")

  def __delete_user(self):
    user_id = Menu.__prompt_user_id_or_none()

    if user_id is None:
      return

    deleted = self.storage.delete(user_id)

    print("User is successfully deleted" if deleted else Menu.__make_user_with_id_not_found_message(user_id))

  def __delete_all_users(self):
    self.storage.delete_all()

    print("All users all successfully deleted")

  @staticmethod
  def __make_user_with_id_not_found_message(user_id: int) -> str:
    return f"User with id {user_id} not found"

  @staticmethod
  def __prompt_user_id_or_none() -> int | None:
    return prompt_int_or_none("Enter user id (or nothing to cancel): ")
