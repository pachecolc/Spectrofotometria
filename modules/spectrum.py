"""Synthetic absorption-spectrum utilities."""
from __future__ import annotations

import numpy as np
import pandas as pd

DEFAULT_SPECTRAL_STEP_NM = 5.0


def build_wavelength_grid(start_nm: float = 440.0, stop_nm: float = 800.0, step_nm: float = DEFAULT_SPECTRAL_STEP_NM) -> np.ndarray:
    """Create an inclusive wavelength grid with a user-selectable spectral step."""
    if step_nm <= 0:
        raise ValueError("El paso espectral debe ser mayor que cero.")
    if stop_nm <= start_nm:
        raise ValueError("La longitud de onda final debe ser mayor que la inicial.")
    return np.arange(start_nm, stop_nm + step_nm * 0.5, step_nm, dtype=float)


EXPERIMENTAL_WAVELENGTHS_NM = build_wavelength_grid()


def generate_spectrum(
    lambda0_nm: float = 575.0,
    amplitude: float = 1.0,
    sigma_nm: float = 35.0,
    noise_sd: float = 0.0,
    seed: int = 42,
    wavelengths_nm: np.ndarray | None = None,
    step_nm: float = DEFAULT_SPECTRAL_STEP_NM,
) -> pd.DataFrame:
    """Generate a Gaussian educational spectrum with selectable spectral resolution."""
    if amplitude < 0:
        raise ValueError("La amplitud no puede ser negativa.")
    if sigma_nm <= 0:
        raise ValueError("El ancho σ debe ser mayor que cero.")
    if noise_sd < 0:
        raise ValueError("El ruido no puede ser negativo.")
    wavelengths = build_wavelength_grid(step_nm=step_nm) if wavelengths_nm is None else np.asarray(wavelengths_nm, dtype=float)
    absorbance = amplitude * np.exp(-((wavelengths - lambda0_nm) ** 2) / (2.0 * sigma_nm**2))
    if noise_sd > 0:
        rng = np.random.default_rng(seed)
        absorbance = absorbance + rng.normal(0.0, noise_sd, size=wavelengths.size)
    absorbance = np.clip(absorbance, 0.0, None)
    return pd.DataFrame({"Wavelength": wavelengths, "Absorbance": absorbance})


def find_lambda_max(data: pd.DataFrame, wavelength_col: str = "Wavelength", absorbance_col: str = "Absorbance") -> tuple[float, float]:
    """Return wavelength and absorbance at the largest measured absorbance."""
    if data.empty:
        raise ValueError("No hay datos para localizar λmax.")
    clean = data[[wavelength_col, absorbance_col]].dropna().copy()
    if clean.empty:
        raise ValueError("No hay pares válidos de longitud de onda y absorbancia.")
    idx = clean[absorbance_col].astype(float).idxmax()
    return float(clean.loc[idx, wavelength_col]), float(clean.loc[idx, absorbance_col])


def normalize_spectrum_columns(data: pd.DataFrame, wavelength_col: str, absorbance_col: str) -> pd.DataFrame:
    """Return a standardized two-column spectrum DataFrame."""
    df = data[[wavelength_col, absorbance_col]].copy()
    df.columns = ["Wavelength", "Absorbance"]
    df["Wavelength"] = pd.to_numeric(df["Wavelength"], errors="coerce")
    df["Absorbance"] = pd.to_numeric(df["Absorbance"], errors="coerce")
    df = df.dropna().sort_values("Wavelength").reset_index(drop=True)
    if df.empty:
        raise ValueError("El archivo no contiene datos numéricos válidos.")
    return df
