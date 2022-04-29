from abc import abstractmethod
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Iterable, Dict, ClassVar, Type, Callable, Union, List

from justin_utils.util import is_distinct

Context = Any


@dataclass
class Parameter:
    class Action(str, Enum):
        STORE_TRUE = "store_true"

    name: str = None
    flags: Iterable[str] = None
    nargs: str = None
    default: Any = None
    action: Action = None
    type: Union[Type, Callable[[str], Any]] = None
    choices: Iterable[str] = None

    not_kw_fields: ClassVar[Iterable[str]] = [
        "name",
        "flags",
    ]

    def __post_init__(self):
        if self.flags is None:
            self.flags = ()
        else:
            self.flags = tuple(self.flags)

        if self.action is not None:
            self.action = self.action.value

    @property
    def name_or_flags(self) -> Iterable[str]:
        # noinspection PyTypeChecker
        return tuple(i for i in (self.name,) + self.flags if i)

    @property
    def params(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if k not in Parameter.not_kw_fields and v}


class Action:
    @property
    def parameters(self) -> List[Parameter]:
        return []

    @abstractmethod
    def perform(self, args: Namespace, context: Context) -> None:
        pass


class Command:

    def __init__(self, name: str, actions: Iterable[Action], allowed_same_parameters: Iterable[str] = ()) -> None:
        super().__init__()

        name = name.strip()

        assert " " not in name

        params_set = set()

        for action in actions:
            for param in action.parameters:
                param_name = param.name_or_flags

                assert param_name not in params_set or any(i in allowed_same_parameters for i in param_name)

                params_set.add(param_name)

        self.__name = name
        self.__actions = actions

    @property
    def name(self) -> str:
        return self.__name

    def configure_parser(self, parser_adder):
        subparser: ArgumentParser = parser_adder.add_parser(self.__name)

        self.__configure_subparser(subparser)

        self.__setup_callback(subparser)

    def __configure_subparser(self, subparser: ArgumentParser):
        params_set = set()

        for action in self.__actions:
            for parameter in action.parameters:
                if parameter.name_or_flags in params_set:
                    continue

                subparser.add_argument(*parameter.name_or_flags, **parameter.params)
                params_set.add(parameter.name_or_flags)

    def __setup_callback(self, parser: ArgumentParser):
        parser.set_defaults(func=self.run)

    def run(self, args: Namespace, context: Context) -> None:
        for action in self.__actions:
            action.perform(args, context)


class App:
    def __init__(self, commands: Iterable[Command], context: Context = None) -> None:
        super().__init__()

        assert is_distinct([command.name for command in commands])

        self.__commands = commands
        self.__context = context

    def run(self, args: Iterable[str] = None):
        parser = ArgumentParser()

        parser_adder = parser.add_subparsers()

        for command in self.__commands:
            command.configure_parser(parser_adder)

        namespace = parser.parse_args(args)

        if not hasattr(namespace, "func") or not namespace.func or not isinstance(namespace.func, Callable):
            print("no parameters is bad")

            return

        namespace.func(namespace, self.__context)
