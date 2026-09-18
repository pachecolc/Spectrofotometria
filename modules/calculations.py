"""Core scientific calculations for the UV-Visible spectrophotometry lab."""
from __future__ import annotations

import math

METHYLENE_BLUE_MW_G_MOL = 319.8


def calculate_transmittance(intensity_transmitted: float, intensity_incident: float) -> float:
    """Return T = I / I0 after validating the physical constraints."""
    if intensity_incident <= 0:
        raise ValueError("La intensidad incidente I0 debe ser mayor que cero.")
    if intensity_transmitted <= 0:
        raise ValueError("La intensidad transmitida I debe ser mayor que cero.")
    if intensity_transmitted > intensity_incident:
        raise ValueError("I no puede ser mayor que I0 en este modelo.")
    return float(intensity_transmitted / intensity_incident)


def calculate_absorbance(transmittance: float) -> float:
    """Return A = -log10(T)."""
    if not 0 < transmittance <= 1:
        raise ValueError("La transmitancia debe cumplir 0 < T <= 1.")
    return float(-math.log10(transmittance))


def beer_lambert(epsilon_l_mol_cm: float, path_length_cm: float, concentration_mol_l: float) -> float:
    """Return Beer-Lambert absorbance A = epsilon * b * c."""
    if epsilon_l_mol_cm < 0 or path_length_cm < 0 or concentration_mol_l < 0:
        raise ValueError("ε, b y c no pueden ser negativos.")
    return float(epsilon_l_mol_cm * path_length_cm * concentration_mol_l)


def calculate_dilution(c1: float, v1: float, v2_final: float) -> float:
    """Return C2 from C1*V1 = C2*V2, with V2 as the final volume."""
    if c1 < 0 or v1 < 0:
        raise ValueError("C1 y V1 no pueden ser negativos.")
    if v2_final <= 0:
        raise ValueError("El volumen final V2 debe ser mayor que cero.")
    if v1 > v2_final:
        raise ValueError("V1 no puede superar el volumen final V2.")
    return float(c1 * v1 / v2_final)


def mgL_to_molar(concentration_mg_l: float, molecular_weight_g_mol: float = METHYLENE_BLUE_MW_G_MOL) -> float:
    """Convert mg/L to mol/L using mg/L -> g/L -> mol/L."""
    if concentration_mg_l < 0:
        raise ValueError("La concentración no puede ser negativa.")
    if molecular_weight_g_mol <= 0:
        raise ValueError("El peso molecular debe ser mayor que cero.")
    concentration_g_l = concentration_mg_l / 1000.0
    return float(concentration_g_l / molecular_weight_g_mol)


def molar_to_mgL(concentration_mol_l: float, molecular_weight_g_mol: float = METHYLENE_BLUE_MW_G_MOL) -> float:
    """Convert mol/L to mg/L."""
    if concentration_mol_l < 0:
        raise ValueError("La concentración no puede ser negativa.")
    if molecular_weight_g_mol <= 0:
        raise ValueError("El peso molecular debe ser mayor que cero.")
    return float(concentration_mol_l * molecular_weight_g_mol * 1000.0)


def calculate_percentage_error(estimated: float, true_value: float) -> float:
    """Return absolute percentage error relative to a non-zero true value."""
    if true_value == 0:
        raise ValueError("No se puede calcular error porcentual con valor real igual a cero.")
    return float(abs(estimated - true_value) / abs(true_value) * 100.0)


def concentration_to_mg_l(value: float, unit: str, molecular_weight_g_mol: float = METHYLENE_BLUE_MW_G_MOL) -> float:
    """Convert a supported concentration unit to mg/L."""
    if value < 0:
        raise ValueError("La concentración no puede ser negativa.")
    unit = unit.strip()
    if unit == "mg/L":
        return float(value)
    if unit == "g/L":
        return float(value * 1000.0)
    if unit == "mol/L":
        return molar_to_mgL(value, molecular_weight_g_mol)
    if unit == "mM":
        return molar_to_mgL(value / 1000.0, molecular_weight_g_mol)
    if unit in {"µM", "uM"}:
        return molar_to_mgL(value / 1_000_000.0, molecular_weight_g_mol)
    raise ValueError(f"Unidad no soportada: {unit}")


def mg_l_to_unit(value_mg_l: float, unit: str, molecular_weight_g_mol: float = METHYLENE_BLUE_MW_G_MOL) -> float:
    """Convert mg/L to a supported concentration unit."""
    if value_mg_l < 0:
        raise ValueError("La concentración no puede ser negativa.")
    if unit == "mg/L":
        return float(value_mg_l)
    if unit == "g/L":
        return float(value_mg_l / 1000.0)
    mol_l = mgL_to_molar(value_mg_l, molecular_weight_g_mol)
    if unit == "mol/L":
        return mol_l
    if unit == "mM":
        return float(mol_l * 1000.0)
    if unit in {"µM", "uM"}:
        return float(mol_l * 1_000_000.0)
    raise ValueError(f"Unidad no soportada: {unit}")
