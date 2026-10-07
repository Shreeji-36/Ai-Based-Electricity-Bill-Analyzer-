import numpy as np
from sklearn.linear_model import Ridge


def _features(t: np.ndarray) -> np.ndarray:
    return np.column_stack([t, np.sin(2 * np.pi * t / 12), np.cos(2 * np.pi * t / 12)])


def forecast_units(history: list[float], months: int = 3) -> dict:
    """history: monthly units, oldest to newest."""
    y = np.array(history, dtype=float)
    n = len(y)
    if n < 3:
        base = float(y[-1]) if n else 0.0
        mid = [base] * months
        band = base * 0.10
        method = "flat"
    else:
        t = np.arange(n, dtype=float)
        future = np.arange(n, n + months, dtype=float)
        if n >= 6:
            model = Ridge(alpha=1.0).fit(_features(t), y)
            fitted, mid = model.predict(_features(t)), model.predict(_features(future))
            method = "ridge-seasonal"
        else:
            slope, icpt = np.polyfit(t, y, 1)
            fitted, mid = slope * t + icpt, slope * future + icpt
            method = "linear-trend"
        band = 1.28 * float(np.std(y - fitted)) or float(y.mean()) * 0.05
    mid = np.clip(mid, 0, None)
    return {
        "method": method,
        "units": [round(float(v)) for v in mid],
        "low": [round(max(float(v) - band, 0)) for v in mid],
        "high": [round(float(v) + band) for v in mid],
    }