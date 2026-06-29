import pytest

from justin_utils.transfer import TransferSpeedMeter


def test_feed_before_start_raises():
    meter = TransferSpeedMeter()
    with pytest.raises(AssertionError):
        meter.feed(1024)


def test_average_value_before_start_raises():
    meter = TransferSpeedMeter()
    with pytest.raises(AssertionError):
        _ = meter.average_value


def test_average_value_after_feed_but_without_start_raises():
    # feed itself raises before we even get to average_value
    meter = TransferSpeedMeter()
    with pytest.raises(AssertionError):
        meter.feed(512)
    with pytest.raises(AssertionError):
        _ = meter.average_value


def test_current_value_after_start_and_feed():
    meter = TransferSpeedMeter()
    meter.start()
    meter.feed(1024)
    speed = meter.current_value
    assert speed is not None


def test_average_value_after_start_and_feed():
    meter = TransferSpeedMeter()
    meter.start()
    meter.feed(1024)
    speed = meter.average_value
    assert speed is not None


def test_multiple_feeds():
    meter = TransferSpeedMeter()
    meter.start()
    for size in [512, 1024, 2048, 4096, 8192, 16384]:
        meter.feed(size)
    speed = meter.average_value
    assert speed is not None
