import logging
from abc import abstractmethod
from collections.abc import Callable, Mapping
from dataclasses import MISSING, Field, asdict, dataclass, fields
from types import NoneType, UnionType
from typing import Any, Self, TypeVar, cast, get_args, get_origin

log = logging.getLogger("justin_utils.dictable")

V = TypeVar("V")

Json = None | bool | int | float | str | list["Json"] | dict[str, "Json"]

Rules = Mapping[type, Callable[[Json], Any]]


class Dictable:
    @classmethod
    def rules(cls) -> Rules:
        return {}

    @classmethod
    def from_dict(cls, json_object: Json) -> Self:
        return fromdict(json_object, cls, cls.rules())

    @abstractmethod
    def as_dict(self) -> Mapping[str, Any]:
        pass


@dataclass
class DictableDataclass(Dictable):
    def as_dict(self) -> Mapping[str, Any]:
        return asdict(self)


def _unwrap_optional(field_type: Any) -> tuple[Any, bool]:
    """Возвращает тип без None и признак того, что None допустим."""
    if get_origin(field_type) is not UnionType:
        return field_type, False

    args = get_args(field_type)
    optional = NoneType in args
    without_none = tuple(arg for arg in args if arg is not NoneType)

    if len(without_none) != 1:
        return field_type, optional

    return without_none[0], optional


def _convert(value: Json, field_type: Any, rules: Rules) -> Any:
    if field_type in rules:
        return rules[field_type](value)

    origin = get_origin(field_type)

    if origin in (list, tuple) and isinstance(value, list):
        args = get_args(field_type)
        element_type = args[0] if args else Any

        return origin(_convert(item, element_type, rules) for item in value)

    if isinstance(field_type, type) and issubclass(field_type, Dictable):
        return field_type.from_dict(value)

    if field_type is Any:
        return value

    return field_type(value)


def _default(field: Field) -> Any:
    if field.default_factory is not MISSING:
        return field.default_factory()

    if field.default is not MISSING:
        return field.default

    return None


def fromdict(obj: Json, data_class: type[V], rules: Rules | None = None) -> V:
    name = data_class.__name__

    if not isinstance(obj, dict):
        raise TypeError(f"{name} ожидает объект, получен {type(obj).__name__}")

    rules = rules or {}

    result: dict[str, Any] = {}

    for field in fields(cast(Any, data_class)):
        field_type, optional = _unwrap_optional(field.type)

        if field.name not in obj:
            result[field.name] = _default(field)
            log.debug("%s.%s отсутствует, дефолт", name, field.name)

            continue

        if obj[field.name] is None and optional:
            result[field.name] = None
            log.debug("%s.%s пришло null", name, field.name)

            continue

        try:
            result[field.name] = _convert(obj[field.name], field_type, rules)
        except (TypeError, ValueError) as e:
            fallback = _default(field)
            result[field.name] = fallback

            log.warning(
                "%s.%s: не удалось привести %r к %s (%s), дефолт %r",
                name,
                field.name,
                obj[field.name],
                field_type,
                e,
                fallback,
            )

    return data_class(**result)
