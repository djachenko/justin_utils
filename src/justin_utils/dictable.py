import json
import logging
from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping
from dataclasses import MISSING, Field, asdict, fields, is_dataclass
from json import JSONDecodeError
from pathlib import Path
from types import NoneType, UnionType
from typing import Any, ClassVar, Protocol, Self, TypeVar, get_args, get_origin

log = logging.getLogger("justin_utils.dictable")

Json = None | bool | int | float | str | list["Json"] | dict[str, "Json"]

Rules = Mapping[type, Callable[[Json], Any]]


class DataclassLike(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]


V = TypeVar("V", bound=DataclassLike)


class DictableError(Exception):
    def __init__(self, path: str, message: str) -> None:
        super().__init__(f"{path}: {message}")

        self.path = path
        self.message = message


class Dictable(ABC):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]

    @classmethod
    def rules(cls) -> Rules:
        return {}

    @classmethod
    def from_dict(cls, json_object: Json) -> Self:
        return fromdict(json_object, cls)

    @abstractmethod
    def as_dict(self) -> Mapping[str, Any]:
        pass


class DictableDataclass(Dictable):
    def as_dict(self) -> Mapping[str, Any]:
        if not is_dataclass(self):
            raise TypeError(f"{type(self).__name__} is not a dataclass")

        return asdict(self)


def _unwrap_optional(field_type: Any) -> tuple[Any, bool]:
    """Returns the type without None and a flag telling whether None is allowed."""
    if get_origin(field_type) is not UnionType:
        return field_type, False

    args = get_args(field_type)
    optional = NoneType in args
    without_none = tuple(arg for arg in args if arg is not NoneType)

    if len(without_none) != 1:
        return field_type, optional

    return without_none[0], optional


def _rule(field_type: Any, rules: Rules) -> Callable[[Json], Any] | None:
    """Looks a rule up along the MRO: a rule for a base type also applies to its subclasses."""
    if get_origin(field_type) is not None or not isinstance(field_type, type):
        return None

    for base in field_type.__mro__:
        if base in rules:
            return rules[base]

    return None


def _has_default(field: Field) -> bool:
    return field.default_factory is not MISSING or field.default is not MISSING


def _default(field: Field) -> Any:
    if field.default_factory is not MISSING:
        return field.default_factory()

    return field.default


def _convert(value: Json, field_type: Any, rules: Rules, effective: Rules, path: str) -> Any:
    rule = _rule(field_type, effective)

    if rule is not None:
        try:
            return rule(value)
        except (TypeError, ValueError) as e:
            raise DictableError(path, f"rule for {field_type} rejected {value!r}: {e}") from e

    origin = get_origin(field_type)

    if origin in (list, tuple):
        if not isinstance(value, list):
            raise DictableError(path, f"expected a list, got {type(value).__name__}")

        args = get_args(field_type)
        element_type = args[0] if args else Any

        return origin(
            _convert(item, element_type, rules, effective, f"{path}[{index}]") for index, item in enumerate(value)
        )

    if isinstance(field_type, type) and issubclass(field_type, Dictable):
        return _fromdict(value, field_type, rules, path)

    if field_type is Any:
        return value

    try:
        return field_type(value)
    except (TypeError, ValueError) as e:
        raise DictableError(path, f"cannot convert {value!r} to {field_type}: {e}") from e


def _effective(data_class: type, rules: Rules) -> Rules:
    """A class's own rules take precedence over the general ones passed in."""
    if not issubclass(data_class, Dictable):
        return rules

    own = data_class.rules()

    if not own:
        return rules

    return {**rules, **own}


def _fromdict[V: DataclassLike](obj: Json, data_class: type[V], rules: Rules, path: str) -> V:
    if not isinstance(obj, dict):
        raise DictableError(path, f"expected an object, got {type(obj).__name__}")

    effective = _effective(data_class, rules)

    result: dict[str, Any] = {}

    for field in fields(data_class):
        field_path = f"{path}.{field.name}"
        field_type, optional = _unwrap_optional(field.type)

        if field.name not in obj:
            if not _has_default(field):
                raise DictableError(field_path, "field is missing and has no default")

            result[field.name] = _default(field)

            log.debug("%s is missing, using default", field_path)

            continue

        value = obj[field.name]

        if value is None:
            if not optional:
                raise DictableError(field_path, "null in a field that does not allow None")

            result[field.name] = None

            continue

        result[field.name] = _convert(value, field_type, rules, effective, field_path)

    return data_class(**result)


def fromdict[V: DataclassLike](obj: Json, data_class: type[V], rules: Rules | None = None) -> V:
    return _fromdict(obj, data_class, rules or {}, data_class.__name__)


def frompath[V: DataclassLike](path: Path, data_class: type[V], rules: Rules | None = None) -> V:
    try:
        return fromdict(json.loads(path.read_text()), data_class, rules)
    except (JSONDecodeError, UnicodeDecodeError) as error:
        raise DictableError(str(path), f"invalid json: {error}") from error
    except DictableError as error:
        raise DictableError(f"{path} → {error.path}", error.message) from error
