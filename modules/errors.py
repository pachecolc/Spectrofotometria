"""Pedagogical models of common spectrophotometric errors."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ErrorConfig:
    instrument_noise: bool = False
    pipetting_error: bool = False
    fingerprints: bool = False
    bubble: bool = False
    wrong_blank: bool = False
    stray_light: bool = False
    high_concentration_nonlinearity: bool = False
    noise_sd: float = 0.01
    pipetting_relative_sd: float = 0.02
    fingerprint_offset: float = 0.025
    blank_offset: float = 0.020
    stray_light_fraction: float = 0.002
    nonlinearity_alpha: float = 0.018


def simulate_pipetting_error(concentrations: np.ndarray, rng: np.random.Generator, relative_sd: float = 0.02) -> np.ndarray:
    """Perturb non-zero prepared concentrations with small relative pipetting error."""
    concentrations = np.asarray(concentrations, dtype=float)
    perturbation = rng.normal(0.0, relative_sd, size=concentrations.size)
    actual = concentrations * (1.0 + perturbation)
    actual[concentrations == 0] = 0.0
    return np.clip(actual, 0.0, None)


def simulate_instrument_noise(absorbance: np.ndarray, rng: np.random.Generator, noise_sd: float = 0.01) -> np.ndarray:
    """Add small Gaussian instrumental noise."""
    return np.asarray(absorbance, dtype=float) + rng.normal(0.0, noise_sd, size=np.asarray(absorbance).size)


def simulate_blank_error(absorbance: np.ndarray, offset: float = 0.02) -> np.ndarray:
    """Apply a constant baseline displacement representing an incorrect blank."""
    return np.asarray(absorbance, dtype=float) + offset


def apply_stray_light(absorbance: np.ndarray, stray_fraction: float = 0.002) -> np.ndarray:
    """Compress high absorbances using a simple stray-light transmittance model."""
    a = np.asarray(absorbance, dtype=float)
    true_t = 10.0 ** (-np.clip(a, 0.0, None))
    measured_t = (true_t + stray_fraction) / (1.0 + stray_fraction)
    return -np.log10(np.clip(measured_t, 1e-12, 1.0))


def apply_high_concentration_nonlinearity(absorbance: np.ndarray, concentrations: np.ndarray, alpha: float = 0.018) -> np.ndarray:
    """Introduce a mild downward deviation from linearity at high concentration."""
    a = np.asarray(absorbance, dtype=float)
    c = np.asarray(concentrations, dtype=float)
    return a / (1.0 + alpha * np.maximum(c, 0.0))


def apply_experimental_errors(
    nominal_concentrations: np.ndarray,
    theoretical_absorbance: np.ndarray,
    config: ErrorConfig,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray, dict[str, float | int | str]]:
    """Apply selected errors reproducibly and return actual concentrations and readings."""
    rng = np.random.default_rng(seed)
    nominal = np.asarray(nominal_concentrations, dtype=float)
    actual_c = nominal.copy()
    measured_a = np.asarray(theoretical_absorbance, dtype=float).copy()
    notes: list[str] = []

    if config.pipetting_error:
        actual_c = simulate_pipetting_error(nominal, rng, config.pipetting_relative_sd)
        notes.append("error de pipeteo")
        # Preserve a non-zero intercept by reconstructing the linear baseline at the
        # actually prepared concentration instead of scaling the whole absorbance.
        if nominal.size >= 2 and np.ptp(nominal) > 0:
            slope, intercept = np.polyfit(nominal, measured_a, 1)
            measured_a = slope * actual_c + intercept

    if config.high_concentration_nonlinearity:
        measured_a = apply_high_concentration_nonlinearity(measured_a, actual_c, config.nonlinearity_alpha)
        notes.append("pérdida de linealidad a concentración alta")
    if config.stray_light:
        measured_a = apply_stray_light(measured_a, config.stray_light_fraction)
        notes.append("luz parásita")
    if config.wrong_blank:
        measured_a = simulate_blank_error(measured_a, config.blank_offset)
        notes.append("blanco incorrecto")
    if config.fingerprints:
        measured_a = measured_a + config.fingerprint_offset
        notes.append("huellas en cubeta")
    if config.instrument_noise:
        measured_a = simulate_instrument_noise(measured_a, rng, config.noise_sd)
        notes.append("ruido instrumental")
    if config.bubble and measured_a.size:
        idx = int(rng.integers(0, measured_a.size))
        measured_a[idx] += float(rng.normal(0.0, max(config.noise_sd * 4.0, 0.035)))
        notes.append(f"burbuja en lectura {idx + 1}")

    measured_a = np.clip(measured_a, 0.0, None)
    metadata = {
        "n_effects": len(notes),
        "effects": ", ".join(notes) if notes else "ninguno",
    }
    return actual_c, measured_a, metadata
