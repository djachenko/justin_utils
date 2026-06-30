import pytest

from justin_utils.singleton import Singleton


class _ConcreteSingleton(Singleton):
    pass


class _OtherSingleton(Singleton):
    pass


class TestSingleton:
    def test_direct_instantiation_raises(self):
        with pytest.raises(AssertionError):
            _ConcreteSingleton()

    def test_instance_returns_same_object(self):
        first = _ConcreteSingleton.instance()
        second = _ConcreteSingleton.instance()

        assert first is second

    def test_instance_is_cached_per_subclass(self):
        concrete = _ConcreteSingleton.instance()
        other = _OtherSingleton.instance()

        assert concrete is not other
        assert isinstance(concrete, _ConcreteSingleton)
        assert isinstance(other, _OtherSingleton)
