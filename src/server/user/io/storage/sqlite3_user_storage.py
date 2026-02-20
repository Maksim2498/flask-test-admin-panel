import sqlite3
from collections.abc import Iterable
from os.path import dirname
from typing import cast, override

from common.io.storage import Storage
from common.user import Admin, Moderator, User

__all__ = ["Sqlite3UserStorage"]


class Sqlite3UserStorage(Storage[User]):
  __database: str

  def __init__(self, database: str = "users.sqlite3"):
    super().__init__()

    self.__database = database

    schema_script_path = f"{dirname(__file__)}/schema.sql"
    with open(schema_script_path) as f:
      schema_script = f.read()

    with self.__connect() as connection:
      connection.executescript(schema_script)

  @property
  def database(self) -> str:
    return self.__database

  @override
  def persist(self, obj: User) -> int:
    return self.__insert(obj) if obj.id < 0 else self.__update(obj)

  def __insert(self, user: User) -> int:
    with self.__connect() as connection:
      cursor = connection.cursor()

      cursor.execute("BEGIN")

      Sqlite3UserStorage.__insert_to_users(cursor, user)

      user._id = cast(int, cursor.lastrowid)

      if isinstance(user, Moderator):
        Sqlite3UserStorage.__insert_to_moderators(cursor, user)
        Sqlite3UserStorage.__insert_verified_users(cursor, user)

      if isinstance(user, Admin):
        Sqlite3UserStorage.__insert_to_admins(cursor, user)
        Sqlite3UserStorage.__insert_created_pages(cursor, user)

      cursor.execute("COMMIT")

      return user.id

  def __update(self, user: User) -> int:
    with self.__connect() as connection:
      cursor = connection.cursor()

      cursor.execute("BEGIN")

      Sqlite3UserStorage.__update_user(cursor, user)

      if isinstance(user, Moderator):
        Sqlite3UserStorage.__delete_verified_users(cursor, user)
        Sqlite3UserStorage.__insert_verified_users(cursor, user)

      if isinstance(user, Admin):
        Sqlite3UserStorage.__delete_created_pages(cursor, user)
        Sqlite3UserStorage.__insert_created_pages(cursor, user)

      cursor.execute("COMMIT")

      return user.id

  @staticmethod
  def __update_user(cursor: sqlite3.Cursor, user: User):
    cursor.execute(
      """
                UPDATE
                    User
                SET
                    login = ?,
                    name  = ?
                WHERE
                    id = ?
            """,
      (
        user.login,
        user.name,
        user.id,
      ),
    )

  @staticmethod
  def __insert_to_users(cursor: sqlite3.Cursor, user: User):
    cursor.execute(
      """
            INSERT INTO
                User (login, name)
            VALUES
                (?, ?)
        """,
      (user.login, user.name),
    )

  @staticmethod
  def __insert_to_moderators(cursor: sqlite3.Cursor, moderator: Moderator):
    cursor.execute("INSERT INTO Moderator (id) VALUES (?)", (moderator.id,))

  @staticmethod
  def __insert_to_admins(cursor: sqlite3.Cursor, admin: Admin):
    cursor.execute("INSERT INTO Admin (id) VALUES (?)", (admin.id,))

  @staticmethod
  def __delete_verified_users(cursor: sqlite3.Cursor, moderator: Moderator):
    cursor.execute("DELETE FROM VerifiedUser WHERE moderator_id = ?", (moderator.id,))

  @staticmethod
  def __insert_verified_users(cursor: sqlite3.Cursor, moderator: Moderator):
    cursor.executemany(
      """
                INSERT INTO
                    VerifiedUser (moderator_id, user_login)
                VALUES
                    (?, ?)
            """,
      map(
        lambda verified_user: (moderator.id, verified_user),
        moderator._verified_users,
      ),
    )

  @staticmethod
  def __delete_created_pages(cursor: sqlite3.Cursor, admin: Admin):
    cursor.execute("DELETE FROM CreatedPage WHERE admin_id = ?", (admin.id,))

  @staticmethod
  def __insert_created_pages(cursor: sqlite3.Cursor, admin: Admin):
    cursor.executemany(
      """
                INSERT INTO
                    CreatedPage (admin_id, name)
                VALUES
                    (?, ?)
            """,
      map(
        lambda page: (admin.id, page),
        admin._created_pages,
      ),
    )

  @override
  def load(self, user_id: int) -> User | None:
    with self.__connect() as connection:
      cursor = connection.cursor()

      cursor.execute("BEGIN")

      cursor.execute(
        """
                SELECT
                    u.id as user_id,
                    m.id as moderator_id,
                    a.id as admin_id,
                    u.login,
                    u.name
                FROM
                    User u
                LEFT JOIN Moderator m ON
                    u.id = m.id
                LEFT JOIN Admin a ON
                    u.id = a.id
                WHERE
                    u.id = ?
            """,
        (user_id,),
      )

      row = cursor.fetchone()

      if row is None:
        return None

      _, moderator_id, admin_id, login, name = row

      user: User | None = None

      if admin_id is not None:
        user = Admin()

        cursor.execute(
          """
                    SELECT
                        name
                    FROM
                        CreatedPage
                    WHERE
                        admin_id = ?
                """,
          (admin_id,),
        )

        rows = cursor.fetchall()
        pages = map(lambda entry: entry[0], rows)

        user._created_pages = frozenset(pages)

      if moderator_id is not None:
        if user is None:
          user = Moderator()

        cursor.execute(
          """
                    SELECT
                        user_login
                    FROM
                        VerifiedUser
                    WHERE
                        moderator_id = ?
                """,
          (moderator_id,),
        )

        rows = cursor.fetchall()
        users = map(lambda entry: entry[0], rows)

        cast(Moderator, user)._verified_users = frozenset(users)

      if user is None:
        user = User()

      user._id = user_id
      user._login = login
      user._name = name

      cursor.execute("COMMIT")

      return user

  @override
  def load_all_ids(self) -> Iterable[int]:
    with self.__connect() as connection:
      cursor = connection.execute("SELECT id FROM User")
      rows = cursor.fetchall()
      ids = map(lambda entry: entry[0], rows)

      return ids

  @override
  def count(self) -> int:
    with self.__connect() as connection:
      cursor = connection.execute("SELECT COUNT(*) FROM User")
      row = cursor.fetchone()
      count = row[0]

      return count

  @override
  def delete(self, user_id: int) -> bool:
    with self.__connect() as connection:
      cursor = connection.execute("DELETE FROM User WHERE id = ?", (user_id,))
      deleted = cursor.rowcount != 0

      return deleted

  @override
  def delete_all(self):
    with self.__connect() as connection:
      connection.execute("DELETE FROM User")

  def __connect(self) -> sqlite3.Connection:
    return sqlite3.connect(self.__database, isolation_level=None)
