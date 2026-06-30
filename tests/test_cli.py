from argparse import Namespace
from typing import Iterable, List

import pytest

from justin_utils.cli import Action, App, Command, Parameter


class _RecordingAction(Action):
    def __init__(self, parameters: Iterable[Parameter] = ()) -> None:
        self.__parameters = list(parameters)

        self.calls: list[tuple[Namespace, object]] = []

    @property
    def parameters(self) -> List[Parameter]:
        return self.__parameters

    def perform(self, args: Namespace, context: object) -> None:
        self.calls.append((args, context))


class TestParameter:
    @pytest.mark.parametrize("name, flags, expected", [
        ("root", None, ("root",)),
        (None, ["-w", "--width"], ("-w", "--width")),
        ("root", ["-r"], ("root", "-r")),
        (None, None, ()),
    ])
    def test_name_or_flags(self, name, flags, expected):
        parameter = Parameter(name=name, flags=flags)

        assert parameter.name_or_flags == expected

    def test_params_excludes_name_and_flags(self):
        parameter = Parameter(name="count", flags=["-c"], type=int)

        assert parameter.params == {"type": int}

    def test_params_excludes_falsy_values(self):
        parameter = Parameter(name="root", nargs=None, default=None)

        assert parameter.params == {}

    def test_params_includes_truthy_default(self):
        parameter = Parameter(name="root", default=["."])

        assert parameter.params == {"default": ["."]}

    def test_action_enum_converted_to_value(self):
        parameter = Parameter(name="flag", action=Parameter.Action.STORE_TRUE)

        assert parameter.action == "store_true"
        assert parameter.params == {"action": "store_true"}


class TestCommand:
    def test_duplicate_parameter_names_assert(self):
        action1 = _RecordingAction([Parameter(name="root")])
        action2 = _RecordingAction([Parameter(name="root")])

        with pytest.raises(AssertionError):
            Command("cmd", [action1, action2])

    def test_duplicate_parameter_names_allowed_when_whitelisted(self):
        action1 = _RecordingAction([Parameter(name="root")])
        action2 = _RecordingAction([Parameter(name="root")])

        command = Command("cmd", [action1, action2], allowed_same_parameters=["root"])

        assert command.name == "cmd"

    def test_name_with_spaces_asserts(self):
        with pytest.raises(AssertionError):
            Command("bad name", [])

    def test_call_performs_all_actions(self):
        action1 = _RecordingAction()
        action2 = _RecordingAction()
        command = Command("cmd", [action1, action2])

        args = Namespace()
        context = object()

        command(args, context)

        assert action1.calls == [(args, context)]
        assert action2.calls == [(args, context)]


class TestApp:
    def test_duplicate_command_names_assert(self):
        with pytest.raises(AssertionError):
            App([
                Command("cmd", [_RecordingAction()]),
                Command("cmd", [_RecordingAction()]),
            ])

    def test_run_dispatches_to_matching_command(self):
        action = _RecordingAction([Parameter(name="value", type=int)])
        context = object()

        App([Command("cmd", [action])], context=context).run(["cmd", "42"])

        assert len(action.calls) == 1
        called_args, called_context = action.calls[0]
        assert called_args.value == 42
        assert called_context is context

    def test_run_no_args_prints_message(self, capsys):
        App([Command("cmd", [_RecordingAction()])]).run([])

        assert "No parameters is bad" in capsys.readouterr().out
