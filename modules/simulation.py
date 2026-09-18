"""Shared simulation and export helpers."""
from __future__ import annotations

from io import BytesIO

import numpy as np
import pandas as pd


def dataframe_to_excel_bytes(data: pd.DataFrame, sheet_name: str = "Datos") -> bytes:
    """Export a DataFrame to XLSX bytes using openpyxl."""
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        data.to_excel(writer, index=False, sheet_name=sheet_name[:31])
    return buffer.getvalue()


def generate_unknown_concentration(seed: int, mode: str = "Interpolación") -> float:
    """Generate a reproducible unknown concentration in or outside calibration range."""
    rng = np.random.default_rng(seed)
    if mode == "Extrapolación":
        return float(rng.uniform(10.8, 14.0))
    return float(rng.uniform(0.8, 9.2))


def simulate_unknown_absorbance(
    concentration_mg_l: float,
    slope: float,
    intercept: float,
    seed: int,
    noise_sd: float = 0.006,
) -> float:
    """Generate an unknown-sample absorbance from a calibration relation plus small noise."""
    rng = np.random.default_rng(seed)
    value = slope * concentration_mg_l + intercept + rng.normal(0.0, max(noise_sd, 0.0))
    return float(max(value, 0.0))


def build_html_report(title: str, summary: pd.DataFrame, records: pd.DataFrame | None = None) -> str:
    """Create a lightweight downloadable HTML report."""
    records_html = "<p>No hay mediciones registradas.</p>" if records is None or records.empty else records.to_html(index=False, border=0)
    return f"""<!doctype html>
<html lang='es'><head><meta charset='utf-8'><title>{title}</title>
<style>body{{font-family:Arial,sans-serif;max-width:1000px;margin:40px auto;line-height:1.5}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #ddd;padding:8px;text-align:left}}th{{background:#f5f7fa}}</style>
</head><body><h1>{title}</h1><h2>Resumen</h2>{summary.to_html(index=False, border=0)}<h2>Mediciones registradas</h2>{records_html}<p><em>Datos simulados con fines educativos cuando corresponda.</em></p></body></html>"""
