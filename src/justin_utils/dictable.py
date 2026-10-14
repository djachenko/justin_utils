import json
import logging
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import MISSING, Field, asdict, fields, is_dataclass
from json import JSONDecodeError
from pathlib import Path
from types import NoneType, UnionType
from typing import Annotated, Any, ClassVar, Protocol, Self, TypeVar, Union, get_args, get_origin

log = logging.getLogger("justin_utils.dictable")

Json = None | bool | int | float | str | list["Json"] | dict[str, "Json"]

Rules = Mapping[type, Callable[[Json], Any]]


class DataclassLike(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]


V = TypeVar("V", bound=DataclassLike)


class DictableError(Exception):
    """The path is assembled while the error unwinds: `tail` grows field by field, `root` names the outermost class."""

    def __init__(self, path: str, message: str) -> None:
        super().__init__(path, message)

        self.root = path
        self.tail = ""
        self.message = message

    @property
    def path(self) -> str:
        return f"{self.root}{self.tail}"

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


class Dictable(ABC):
    @classmethod
    @abstractmethod
    def from_dict(cls, json_object: Json, rules: Rules | None = None) -> Self:
        pass

    @abstractmethod
    def as_dict(self) -> Mapping[str, Any]:
        pass


class DictableDataclass(Dictable):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]

    @classmethod
    def from_dict(cls, json_object: Json, rules: Rules | None = None) -> Self:
        return fromdict(json_object, cls, rules)

    def as_dict(self) -> Mapping[str, Any]:
        if not is_dataclass(self):
            raise TypeError(f"{type(self).__name__} is not a dataclass")

        return asdict(self)


def _unwrap_optional(field_type: Any) -> tuple[Any, bool]:
    """Returns the type without None and a flag telling whether None is allowed."""
    origin = get_origin(field_type)

    if origin is Annotated:
        inner_type, *metadata = get_args(field_type)
        unwrapped, optional = _unwrap_optional(inner_type)

        return Annotated[unwrapped, *metadata], optional

    if origin not in (UnionType, Union):
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


@contextmanager
def _segment(segment: str) -> Iterator[None]:
    """Prepends a path segment to a DictableError passing through, so the path is built on the way back."""
    try:
        yield
    except DictableError as error:
        error.tail = f"{segment}{error.tail}"

        raise


def _parse(parser: Callable[[Json], Any], value: Json, name: str) -> Any:
    try:
        return parser(value)
    except (TypeError, ValueError) as e:
        raise DictableError("", f"{name} rejected {value!r}: {e}") from e


def _convert(value: Json, field_type: Any, rules: Rules) -> Any:
    origin = get_origin(field_type)

    if origin is Annotated:
        inner_type, parser, *_ = get_args(field_type)

        return _parse(parser, value, f"parser for {inner_type}")

    rule = _rule(field_type, rules)

    if rule is not None:
        return _parse(rule, value, f"rule for {field_type}")

    if origin in (list, tuple):
        if not isinstance(value, list):
            raise DictableError("", f"expected a list, got {type(value).__name__}")

        args = get_args(field_type)
        element_type = args[0] if args else Any
        items = []

        for index, item in enumerate(value):
            with _segment(f"[{index}]"):
                items.append(_convert(item, element_type, rules))

        return origin(items)

    if isinstance(field_type, type):
        if issubclass(field_type, Dictable):
            return field_type.from_dict(value, rules)

        if is_dataclass(field_type):
            return fromdict(value, field_type, rules)

    if field_type is Any:
        return value

    try:
        return field_type(value)
    except (TypeError, ValueError) as e:
        raise DictableError("", f"cannot convert {value!r} to {field_type}: {e}") from e


def _field_value(obj: dict[str, Json], field: Field, rules: Rules, data_class: type) -> Any:
    field_type, optional = _unwrap_optional(field.type)

    if field.name not in obj:
        if not _has_default(field):
            raise DictableError("", "field is missing and has no default")

        log.debug("%s.%s is missing, using default", data_class.__name__, field.name)

        return _default(field)

    value = obj[field.name]

    if value is None:
        if not optional:
            raise DictableError("", "null in a field that does not allow None")

        return None

    return _convert(value, field_type, rules)


def fromdict(obj: Json, data_class: type[V], rules: Rules | None = None) -> V:
    """Walks the fields itself, never via `data_class.from_dict`: an override calls it to get the default parsing."""
    try:
        if not isinstance(obj, dict):
            raise DictableError("", f"expected an object, got {type(obj).__name__}")

        result: dict[str, Any] = {}
        rules = rules or {}

        for field in fields(data_class):
            with _segment(f".{field.name}"):
                result[field.name] = _field_value(obj, field, rules, data_class)

        return data_class(**result)
    except DictableError as error:
        error.root = data_class.__name__

        raise


def _first_significant_byte(path: Path) -> bytes:
    with path.open("rb") as file:
        while (byte := file.read(1)).isspace():
            pass

        return byte


def frompath(path: Path, data_class: type[V], rules: Rules | None = None) -> V:
    if _first_significant_byte(path) != b"{":
        raise DictableError(str(path), "invalid json: not an object")

    try:
        return fromdict(json.loads(path.read_text()), data_class, rules)
    except (JSONDecodeError, UnicodeDecodeError) as error:
        raise DictableError(str(path), f"invalid json: {error}") from error
    except DictableError as error:
        error.root = f"{path} → {error.root}"

        raise
