"""Quick scientific consistency checks. Run with: python smoke_test.py"""
from __future__ import annotations

import numpy as np

from modules.calculations import calculate_absorbance, calculate_dilution, calculate_transmittance, mgL_to_molar
from modules.calibration import fit_calibration_curve, generate_calibration_data, predict_unknown
from modules.spectrum import find_lambda_max, generate_spectrum


def main() -> None:
    t = calculate_transmittance(50, 100)
    a = calculate_absorbance(t)
    assert np.isclose(t, 0.5)
    assert np.isclose(a, 0.301029995664)

    expected_dilutions = np.array([0, 2, 4, 6, 8, 10], dtype=float)
    obtained = np.array([calculate_dilution(10, v1, 5) for v1 in range(6)])
    assert np.allclose(obtained, expected_dilutions)

    molar = mgL_to_molar(10)
    assert np.isclose(molar, 0.010 / 319.8)

    spectrum = generate_spectrum(lambda0_nm=575, amplitude=1.0, sigma_nm=35, noise_sd=0, seed=42)
    lmax, _ = find_lambda_max(spectrum)
    assert lmax == 575

    calibration = generate_calibration_data(mode="Ideal")
    fit = fit_calibration_curve(calibration, "Concentration_nominal_mg_L", "Absorbance")
    assert np.isclose(fit["slope"], 0.095)
    assert np.isclose(fit["intercept"], 0.010)
    assert np.isclose(fit["r2"], 1.0)

    unknown = predict_unknown(0.485, 0.095, 0.010)
    assert np.isclose(unknown, 5.0)

    print("All scientific smoke tests passed.")


if __name__ == "__main__":
    main()
