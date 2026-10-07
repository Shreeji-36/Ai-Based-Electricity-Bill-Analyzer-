from energy_ai.anomaly import check_bill
from energy_ai.forecast import forecast_units


def test_forecast_short_history_is_flat():
    r = forecast_units([1000, 1100], months=2)
    assert r["method"] == "flat" and r["units"] == [1100, 1100]


def test_forecast_trend_goes_up():
    r = forecast_units([1000, 1100, 1200, 1300], months=2)
    assert r["units"][0] > 1300


def test_forecast_never_negative():
    assert min(forecast_units([300, 200, 100, 50], months=3)["units"]) >= 0


def test_anomaly_detected():
    hist = [1000, 1020, 990, 1010, 1005, 995]
    assert check_bill(hist, 2500)["is_anomaly"] is True
    assert check_bill(hist, 1008)["is_anomaly"] is False


def test_anomaly_needs_history():
    assert check_bill([1000], 5000)["method"] == "insufficient-history"