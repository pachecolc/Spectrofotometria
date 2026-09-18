"""Calibration data generation, regression, residual analysis and molar absorptivity."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import linregress

from .calculations import METHYLENE_BLUE_MW_G_MOL, mgL_to_molar
from .errors import ErrorConfig, apply_experimental_errors

DEFAULT_CALIBRATION_CONCENTRATIONS_MG_L = np.array([0, 2, 4, 6, 8, 10], dtype=float)


def generate_calibration_data(
    concentrations_mg_l: np.ndarray | None = None,
    slope_abs_per_mg_l: float = 0.095,
    intercept_abs: float = 0.010,
    mode: str = "Ideal",
    error_config: ErrorConfig | None = None,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate clearly synthetic calibration data for education."""
    concentrations = (
        DEFAULT_CALIBRATION_CONCENTRATIONS_MG_L.copy()
        if concentrations_mg_l is None
        else np.asarray(concentrations_mg_l, dtype=float)
    )
    if concentrations.size < 2:
        raise ValueError("Se requieren al menos dos estándares.")
    if np.any(concentrations < 0):
        raise ValueError("Las concentraciones no pueden ser negativas.")
    if slope_abs_per_mg_l <= 0:
        raise ValueError("La pendiente simulada debe ser mayor que cero.")

    theoretical = slope_abs_per_mg_l * concentrations + intercept_abs
    actual_c = concentrations.copy()
    measured = theoretical.copy()
    metadata = {"effects": "ninguno"}

    if mode.lower().startswith("experimental"):
        config = error_config or ErrorConfig(instrument_noise=True)
        actual_c, measured, metadata = apply_experimental_errors(concentrations, theoretical, config, seed)

    return pd.DataFrame(
        {
            "Concentration_nominal_mg_L": concentrations,
            "Concentration_actual_mg_L": actual_c,
            "Absorbance_theoretical": theoretical,
            "Absorbance": measured,
            "Data_type": "SIMULACIÓN",
            "Effects": metadata["effects"],
        }
    )


def fit_calibration_curve(data: pd.DataFrame, concentration_col: str, absorbance_col: str) -> dict[str, object]:
    """Fit A = mC + b0 with scipy.stats.linregress."""
    clean = data[[concentration_col, absorbance_col]].copy()
    clean[concentration_col] = pd.to_numeric(clean[concentration_col], errors="coerce")
    clean[absorbance_col] = pd.to_numeric(clean[absorbance_col], errors="coerce")
    clean = clean.dropna()
    if len(clean) < 2:
        raise ValueError("Se requieren al menos dos puntos válidos para la regresión.")
    x = clean[concentration_col].to_numpy(dtype=float)
    y = clean[absorbance_col].to_numpy(dtype=float)
    if np.allclose(x, x[0]):
        raise ValueError("Las concentraciones deben contener al menos dos valores distintos.")
    result = linregress(x, y)
    predicted = result.intercept + result.slope * x
    residuals = y - predicted
    return {
        "slope": float(result.slope),
        "intercept": float(result.intercept),
        "r2": float(result.rvalue**2),
        "stderr": float(result.stderr) if result.stderr is not None else float("nan"),
        "intercept_stderr": float(result.intercept_stderr) if result.intercept_stderr is not None else float("nan"),
        "n": int(len(clean)),
        "x": x,
        "y": y,
        "predicted": predicted,
        "residuals": residuals,
    }


def predict_unknown(absorbance: float, slope: float, intercept: float) -> float:
    """Return c = (A - b0) / m."""
    if not np.isfinite(absorbance):
        raise ValueError("La absorbancia debe ser finita.")
    if not np.isfinite(slope) or abs(slope) < 1e-12:
        raise ValueError("La pendiente de calibración no puede ser cero.")
    if not np.isfinite(intercept):
        raise ValueError("El intercepto debe ser finito.")
    return float((absorbance - intercept) / slope)


def molar_absorptivity_from_calibration(
    concentrations_mg_l: np.ndarray,
    absorbances: np.ndarray,
    path_length_cm: float = 1.0,
    molecular_weight_g_mol: float = METHYLENE_BLUE_MW_G_MOL,
) -> dict[str, float]:
    """Fit A vs mol/L and calculate epsilon = slope / b."""
    if path_length_cm <= 0:
        raise ValueError("La longitud de la cubeta debe ser mayor que cero.")
    molar = np.array([mgL_to_molar(float(c), molecular_weight_g_mol) for c in concentrations_mg_l], dtype=float)
    result = linregress(molar, np.asarray(absorbances, dtype=float))
    epsilon = result.slope / path_length_cm
    return {
        "epsilon_l_mol_cm": float(epsilon),
        "slope_molar": float(result.slope),
        "intercept": float(result.intercept),
        "r2": float(result.rvalue**2),
    }


def normalize_calibration_columns(data: pd.DataFrame, concentration_col: str, absorbance_col: str) -> pd.DataFrame:
    """Return a standardized two-column calibration DataFrame."""
    df = data[[concentration_col, absorbance_col]].copy()
    df.columns = ["Concentration", "Absorbance"]
    df["Concentration"] = pd.to_numeric(df["Concentration"], errors="coerce")
    df["Absorbance"] = pd.to_numeric(df["Absorbance"], errors="coerce")
    df = df.dropna().sort_values("Concentration").reset_index(drop=True)
    if len(df) < 2:
        raise ValueError("El archivo debe contener al menos dos pares numéricos válidos.")
    return df
