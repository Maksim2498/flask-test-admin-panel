from typing                         import Iterable, Match, TypeVar, cast, override
from os.path                        import join as join_paths
from os                             import mkdir, remove as remove_file, listdir
from shutil                         import rmtree

from common.io.storage.identifiable import Identifiable
from common.io.storage.storage      import Storage

import re
import pickle


__all__ = ["PickleStorage"]


T = TypeVar("T", bound = Identifiable)


class PickleStorage(Storage[T]):
    __dirname:          str
    __filename_pattern: str
    __filename_re:      re.Pattern
    __next_id:          int

    def __init__(self, dirname: str = "db", filename_pattern: str = "{id}.pickle"):
        super().__init__()

        self.__dirname          = dirname
        self.__filename_pattern = filename_pattern
        self.__filename_re      = re.compile(filename_pattern.format(id = "(\\d+)"))

        ids                     = list(self.load_all_ids())

        self.__next_id          = 0 if len(ids) == 0 else max(ids) + 1

    @property
    def dirname(self) -> str:
        return self.__dirname

    @property
    def filename_pattern(self) -> str:
        return self.__filename_pattern

    @override
    def persist(self, obj: T) -> int:
        self.__create_dir()

        if obj.id < 0:
            obj._id         = self.__next_id
            self.__next_id += 1

        filepath = self.__create_filepath(obj.id)

        with open(filepath, "wb") as file:
            pickle.dump(obj, file)

        return obj.id

    @override
    def load(self, obj_id: int) -> T | None:
        filepath = self.__create_filepath(obj_id)

        try:
            with open(filepath, "rb") as file:
                return pickle.load(file)
        except FileNotFoundError:
            return None

    @override
    def count(self) -> int:
        try:
            return len(
                list(
                    filter(
                        lambda file: re.match(self.__filename_re, file) is not None,
                        listdir(self.dirname),
                    )
                )
            )
        except FileNotFoundError:
            return 0

    @override
    def load_all_ids(self) -> Iterable[int]:
        try:
            files = listdir(self.dirname)

            return map(
                lambda match: int(match.group(1)),
                cast(
                    Iterable[Match[str]],
                    filter(
                        lambda match: match is not None,
                        map(
                            lambda file: re.match(self.__filename_re, file),
                            files,
                        )
                    )
                )
            )
        except FileNotFoundError:
            return []

    @override
    def delete(self, obj_id: int) -> bool:
        filepath = self.__create_filepath(obj_id)

        try:
            remove_file(filepath)
            return True
        except FileNotFoundError:
            return False

    @override
    def delete_all(self) -> int:
        deleted = self.count()

        try:
            rmtree(self.dirname)
        except FileNotFoundError:
            ...

        return deleted

    def __create_dir(self):
        try:
            mkdir(self.dirname)
        except FileExistsError:
            ...

    def __create_filepath(self, obj_id: int) -> str:
        return join_paths(self.dirname, self.filename_pattern.format(id = obj_id))
