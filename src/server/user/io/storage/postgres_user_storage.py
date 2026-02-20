from collections.abc import Iterable
from os.path import dirname
from typing import cast, override

import psycopg
from psycopg.rows import dict_row

from common.io.storage import Storage
from common.user import Admin, Moderator, User

__all__ = ["PostgresUserStorage"]


class PostgresUserStorage(Storage[User]):
  __conninfo: str

  def __init__(self, conninfo: str):
    super().__init__()
    self.__conninfo = conninfo

    schema_path = f"{dirname(__file__)}/schema.postgres.sql"
    with open(schema_path) as f:
      schema = f.read()

    with self.__connect() as conn:
      with conn.transaction():
        for stmt in schema.split(";"):
          stmt = stmt.strip()
          if stmt:
            conn.execute(stmt)

  @property
  def conninfo(self) -> str:
    return self.__conninfo

  @override
  def persist(self, obj: User) -> int:
    return self.__insert(obj) if obj.id < 0 else self.__update(obj)

  def __insert(self, user: User) -> int:
    with self.__connect() as conn:
      with conn.transaction():
        row = conn.execute(
          """
            INSERT INTO "User" (login, name)
            VALUES (%s, %s)
            RETURNING id
          """,
          (user.login, user.name),
        ).fetchone()
        user._id = cast(int, row["id"])

        if isinstance(user, Moderator):
          self.__insert_to_moderators(conn, user)
          self.__insert_verified_users(conn, user)

        if isinstance(user, Admin):
          self.__insert_to_admins(conn, user)
          self.__insert_created_pages(conn, user)

        return user.id

  def __update(self, user: User) -> int:
    with self.__connect() as conn:
      with conn.transaction():
        conn.execute(
          """
            UPDATE "User"
            SET login = %s, name = %s
            WHERE id = %s
          """,
          (user.login, user.name, user.id),
        )

        if isinstance(user, Moderator):
          self.__delete_verified_users(conn, user)
          self.__insert_verified_users(conn, user)

        if isinstance(user, Admin):
          self.__delete_created_pages(conn, user)
          self.__insert_created_pages(conn, user)

        return user.id

  @staticmethod
  def __insert_to_moderators(conn: psycopg.Connection, moderator: Moderator):
    conn.execute("INSERT INTO Moderator (id) VALUES (%s)", (moderator.id,))

  @staticmethod
  def __insert_to_admins(conn: psycopg.Connection, admin: Admin):
    conn.execute("INSERT INTO Admin (id) VALUES (%s)", (admin.id,))

  @staticmethod
  def __delete_verified_users(conn: psycopg.Connection, moderator: Moderator):
    conn.execute("DELETE FROM VerifiedUser WHERE moderator_id = %s", (moderator.id,))

  @staticmethod
  def __insert_verified_users(conn: psycopg.Connection, moderator: Moderator):
    for login in moderator._verified_users:
      conn.execute(
        """
          INSERT INTO VerifiedUser (moderator_id, user_login)
          VALUES (%s, %s)
          ON CONFLICT (moderator_id, user_login) DO NOTHING
        """,
        (moderator.id, login),
      )

  @staticmethod
  def __delete_created_pages(conn: psycopg.Connection, admin: Admin):
    conn.execute("DELETE FROM CreatedPage WHERE admin_id = %s", (admin.id,))

  @staticmethod
  def __insert_created_pages(conn: psycopg.Connection, admin: Admin):
    for name in admin._created_pages:
      conn.execute(
        """
          INSERT INTO CreatedPage (admin_id, name)
          VALUES (%s, %s)
          ON CONFLICT (admin_id, name) DO NOTHING
        """,
        (admin.id, name),
      )

  @override
  def load(self, user_id: int) -> User | None:
    with self.__connect() as conn:
      with conn.transaction():
        row = conn.execute(
          """
            SELECT
              u.id AS user_id,
              m.id AS moderator_id,
              a.id AS admin_id,
              u.login,
              u.name
            FROM "User" u
            LEFT JOIN Moderator m ON u.id = m.id
            LEFT JOIN Admin a ON u.id = a.id
            WHERE u.id = %s
          """,
          (user_id,),
        ).fetchone()

        if row is None:
          return None

        user_id_val = row["user_id"]
        moderator_id = row["moderator_id"]
        admin_id = row["admin_id"]
        login = row["login"]
        name = row["name"]

        user: User | None = None

        if admin_id is not None:
          user = Admin()
          pages = conn.execute(
            "SELECT name FROM CreatedPage WHERE admin_id = %s",
            (admin_id,),
          ).fetchall()
          user._created_pages = frozenset(r["name"] for r in pages)

        if moderator_id is not None:
          if user is None:
            user = Moderator()
          users = conn.execute(
            "SELECT user_login FROM VerifiedUser WHERE moderator_id = %s",
            (moderator_id,),
          ).fetchall()
          cast(Moderator, user)._verified_users = frozenset(r["user_login"] for r in users)

        if user is None:
          user = User()

        user._id = user_id_val
        user._login = login
        user._name = name

        return user

  @override
  def load_all_ids(self) -> Iterable[int]:
    with self.__connect() as conn:
      rows = conn.execute('SELECT id FROM "User"').fetchall()
      return (r["id"] for r in rows)

  @override
  def count(self) -> int:
    with self.__connect() as conn:
      row = conn.execute('SELECT COUNT(*) AS c FROM "User"').fetchone()
      return cast(int, row["c"])

  @override
  def delete(self, user_id: int) -> bool:
    with self.__connect() as conn:
      result = conn.execute('DELETE FROM "User" WHERE id = %s', (user_id,))
      return result.rowcount > 0

  @override
  def delete_all(self):
    with self.__connect() as conn:
      conn.execute('DELETE FROM "User"')

  def __connect(self) -> psycopg.Connection:
    return psycopg.connect(self.__conninfo, row_factory=dict_row)
