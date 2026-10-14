import sys
from abc import ABC, abstractmethod

if sys.version_info >= (3, 13):
    from warnings import deprecated
else:
    from typing_extensions import deprecated

from justin_utils.singleton import Singleton

Version = int
JsonObject = dict


@deprecated(
    "json_migration.py has no consumers in the ecosystem; confirm it's still needed before relying on it",
)
class JsonMigration(ABC):
    @property
    @abstractmethod
    def version(self) -> Version:
        pass

    @abstractmethod
    def migrate(self, json_object: JsonObject) -> None:
        pass


@deprecated(
    "json_migration.py has no consumers in the ecosystem; confirm it's still needed before relying on it",
)
class JsonMigrator(Singleton):
    __OBJECT_VERSION_KEY = "version"

    def __init__(self) -> None:
        super().__init__()

        self.__migrations: dict[Version, JsonMigration] = {}

    def register(self, migration: JsonMigration) -> None:
        version = migration.version

        assert version not in self.__migrations

        self.__migrations[version] = migration

    def migrate(self, json_object: JsonObject) -> None:
        if JsonMigrator.__OBJECT_VERSION_KEY in json_object:
            version = json_object[JsonMigrator.__OBJECT_VERSION_KEY]
        else:
            version = 0

        eligible_keys = sorted(key for key in self.__migrations if key > version)

        migrations = [self.__migrations[key] for key in eligible_keys]

        for migration in migrations:
            migration.migrate(json_object)

            json_object[JsonMigrator.__OBJECT_VERSION_KEY] = migration.version
