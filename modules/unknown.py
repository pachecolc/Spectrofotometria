"""Unknown-sample evaluation helpers."""
from __future__ import annotations

from .calculations import calculate_percentage_error
from .calibration import predict_unknown


def evaluate_unknown(absorbance: float, slope: float, intercept: float, true_concentration: float) -> dict[str, float]:
    """Estimate unknown concentration and calculate absolute/relative/percentage errors."""
    estimated = predict_unknown(absorbance, slope, intercept)
    absolute_error = abs(estimated - true_concentration)
    relative_error = absolute_error / abs(true_concentration) if true_concentration != 0 else float("nan")
    percentage_error = calculate_percentage_error(estimated, true_concentration) if true_concentration != 0 else float("nan")
    return {
        "estimated_concentration_mg_l": float(estimated),
        "true_concentration_mg_l": float(true_concentration),
        "absolute_error_mg_l": float(absolute_error),
        "relative_error": float(relative_error),
        "percentage_error": float(percentage_error),
    }
