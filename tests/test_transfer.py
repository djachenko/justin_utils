import pytest

from justin_utils.transfer import TransferSpeedMeter


class TestTransferSpeedMeter:
    @pytest.mark.parametrize("action", [
        lambda meter: meter.feed(1024),
        lambda meter: getattr(meter, "average_value"),
        lambda meter: getattr(meter, "current_value"),
    ])
    def test_action_before_start_raises(self, action):
        meter = TransferSpeedMeter()

        with pytest.raises(AssertionError):
            action(meter)

    @pytest.mark.parametrize("feeds", [
        [1024],
        [512, 1024, 2048, 4096, 8192, 16384],
    ])
    def test_current_value_after_start_and_feed(self, feeds):
        meter = TransferSpeedMeter()
        meter.start()

        for size in feeds:
            meter.feed(size)

        assert meter.current_value is not None

    @pytest.mark.parametrize("feeds", [
        [1024],
        [512, 1024, 2048, 4096, 8192, 16384],
    ])
    def test_average_value_after_start_and_feed(self, feeds):
        meter = TransferSpeedMeter()
        meter.start()

        for size in feeds:
            meter.feed(size)

        assert meter.average_value is not None
