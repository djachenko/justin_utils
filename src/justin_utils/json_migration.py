from abc import ABC, abstractmethod

from justin_utils.singleton import Singleton

Version = int
JsonObject = dict


class JsonMigration(ABC):
    @property
    @abstractmethod
    def version(self) -> Version:
        pass

    @abstractmethod
    def migrate(self, json_object: JsonObject) -> None:
        pass


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
