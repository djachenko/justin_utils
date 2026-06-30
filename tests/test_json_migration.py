import pytest

from justin_utils.json_migration import JsonMigration, JsonMigrator


class _Migration(JsonMigration):
    def __init__(self, version: int, marker: str) -> None:
        self.__version = version
        self.__marker = marker

    @property
    def version(self) -> int:
        return self.__version

    def migrate(self, json_object: dict) -> None:
        json_object.setdefault("applied", []).append(self.__marker)


@pytest.fixture
def migrator():
    # JsonMigrator is a Singleton cached per-class, so each test gets an isolated subclass.
    subclass = type("_Migrator", (JsonMigrator,), {})

    return subclass.instance()


class TestJsonMigrator:
    def test_register_duplicate_version_asserts(self, migrator):
        migrator.register(_Migration(1, "a"))

        with pytest.raises(AssertionError):
            migrator.register(_Migration(1, "b"))

    def test_migrate_applies_migrations_above_current_version(self, migrator):
        migrator.register(_Migration(1, "a"))
        migrator.register(_Migration(2, "b"))

        json_object = {"version": 1}
        migrator.migrate(json_object)

        assert json_object["applied"] == ["b"]

    def test_migrate_without_version_defaults_to_zero(self, migrator):
        migrator.register(_Migration(1, "a"))

        json_object = {}
        migrator.migrate(json_object)

        assert json_object["applied"] == ["a"]

    def test_migrate_applies_in_ascending_version_order(self, migrator):
        migrator.register(_Migration(3, "c"))
        migrator.register(_Migration(1, "a"))
        migrator.register(_Migration(2, "b"))

        json_object = {}
        migrator.migrate(json_object)

        assert json_object["applied"] == ["a", "b", "c"]

    def test_migrate_updates_version_to_latest_applied(self, migrator):
        migrator.register(_Migration(1, "a"))
        migrator.register(_Migration(2, "b"))

        json_object = {}
        migrator.migrate(json_object)

        assert json_object["version"] == 2

    def test_migrate_no_eligible_migrations_is_noop(self, migrator):
        migrator.register(_Migration(1, "a"))

        json_object = {"version": 1}
        migrator.migrate(json_object)

        assert "applied" not in json_object
