from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from modules.calculations import (
    METHYLENE_BLUE_MW_G_MOL,
    beer_lambert,
    calculate_absorbance,
    calculate_dilution,
    calculate_transmittance,
    mgL_to_molar,
)
from modules.calibration import (
    DEFAULT_CALIBRATION_CONCENTRATIONS_MG_L,
    fit_calibration_curve,
    generate_calibration_data,
    molar_absorptivity_from_calibration,
    normalize_calibration_columns,
)
from modules.errors import ErrorConfig
from modules.quiz import render_lab_questionnaire, render_quiz
from modules.simulation import (
    build_html_report,
    dataframe_to_excel_bytes,
    generate_unknown_concentration,
    simulate_unknown_absorbance,
)
from modules.spectrum import find_lambda_max, generate_spectrum, normalize_spectrum_columns
from modules.theory import render_key_concepts, render_theory_content
from modules.unknown import evaluate_unknown

# -----------------------------------------------------------------------------
# Configuration and constants
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Laboratorio Virtual de Espectrofotometría",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

ASSETS = Path("assets")
STOCK_CONCENTRATION_MG_L = 10.0
FINAL_VOLUME_ML = 5.0
PM_METHYLENE_BLUE = METHYLENE_BLUE_MW_G_MOL

NAV_ITEMS = [
    "🏠 Inicio",
    "📘 Fundamento teórico",
    "💡 Luz, transmitancia y absorbancia",
    "🌈 Espectro de absorción",
    "🧪 Preparación de soluciones",
    "📈 Ley de Beer-Lambert",
    "📊 Curva de calibración",
    "❓ Muestra desconocida",
    "⚠️ Errores experimentales",
    "🎯 Laboratorio virtual completo",
    "📝 Autoevaluación",
    "📚 Conceptos clave",
]

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.3rem; padding-bottom: 3rem;}
    .sim-badge {display:inline-block;padding:0.28rem 0.55rem;border-radius:0.45rem;background:#fff3cd;border:1px solid #ffe69c;font-weight:700;}
    .real-badge {display:inline-block;padding:0.28rem 0.55rem;border-radius:0.45rem;background:#d1e7dd;border:1px solid #a3cfbb;font-weight:700;}
    .small-note {font-size:0.9rem;color:#5f6b76;}
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Session state and shared helpers
# -----------------------------------------------------------------------------
def init_state() -> None:
    defaults = {
        "simulation_seed": 42,
        "seed_widget": 42,
        "records": [],
        "unknown_counter": 0,
        "unknown_revealed": False,
        "lab_guidance_visible": False,
        "bl_epsilon": 40000,
        "bl_b": 1.0,
        "bl_c_um": 20.0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_lab() -> None:
    st.session_state.clear()


def new_experiment() -> None:
    next_seed = int(st.session_state.get("seed_widget", st.session_state.get("simulation_seed", 42))) + 1
    st.session_state["seed_widget"] = next_seed
    st.session_state["simulation_seed"] = next_seed
    st.session_state["unknown_counter"] = 0
    st.session_state["unknown_revealed"] = False
    for key in list(st.session_state.keys()):
        if key.startswith("lab_step_") or key.startswith("unknown_state_"):
            del st.session_state[key]
    st.session_state.pop("calibration_state", None)
    st.session_state.pop("spectrum_state", None)


def clear_records() -> None:
    st.session_state["records"] = []


def safe_image(filename: str, caption: str | None = None, width: int | None = None) -> bool:
    path = ASSETS / filename
    if path.exists():
        st.image(str(path), caption=caption, width=width, use_container_width=width is None)
        return True
    st.info(f"Imagen pendiente: {filename}")
    return False


def render_header(title: str, description: str) -> None:
    left, right = st.columns([6, 1])
    with left:
        st.title(title)
        st.caption(description)
    with right:
        logo = ASSETS / "logo_serendipia.png"
        if logo.exists():
            st.image(str(logo), width=110)


def add_record(module: str, condition: str, values: dict[str, object]) -> None:
    records = st.session_state.setdefault("records", [])
    row = {
        "Experimento": len(records) + 1,
        "Módulo": module,
        "Condición": condition,
        "Seed": int(st.session_state["simulation_seed"]),
    }
    row.update(values)
    records.append(row)


def records_dataframe() -> pd.DataFrame:
    return pd.DataFrame(st.session_state.get("records", []))


def read_uploaded_table(uploaded_file) -> pd.DataFrame:
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    if name.endswith(".xlsx") or name.endswith(".xls"):
        return pd.read_excel(uploaded_file)
    raise ValueError("Formato no soportado. Use CSV o XLSX.")


def suggest_column(columns, terms: tuple[str, ...], fallback: int = 0) -> int:
    lowered = [str(c).lower() for c in columns]
    for i, col in enumerate(lowered):
        if any(term in col for term in terms):
            return i
    return min(fallback, max(len(columns) - 1, 0))


def default_calibration_state() -> dict[str, object]:
    if "calibration_state" not in st.session_state:
        df = generate_calibration_data(seed=int(st.session_state["simulation_seed"]))
        fit = fit_calibration_curve(df, "Concentration_nominal_mg_L", "Absorbance")
        st.session_state["calibration_state"] = {
            "data": df,
            "fit": fit,
            "source": "SIMULACIÓN",
            "x_col": "Concentration_nominal_mg_L",
            "y_col": "Absorbance",
        }
    return st.session_state["calibration_state"]


def calibration_plot(data: pd.DataFrame, x_col: str, y_col: str, fit: dict[str, object], title: str) -> go.Figure:
    x = data[x_col].to_numpy(dtype=float)
    y = data[y_col].to_numpy(dtype=float)
    x_line = np.linspace(float(np.min(x)), float(np.max(x)), 200)
    y_line = float(fit["slope"]) * x_line + float(fit["intercept"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="markers", name="Puntos"))
    fig.add_trace(go.Scatter(x=x_line, y=y_line, mode="lines", name="Regresión"))
    fig.update_layout(
        title=title,
        xaxis_title="Concentración de azul de metileno (mg/L)",
        yaxis_title="Absorbancia",
        template="plotly_white",
        legend_title="",
        margin=dict(l=20, r=20, t=60, b=20),
    )
    return fig


def render_simulated_badge() -> None:
    st.markdown('<span class="sim-badge">🟡 DATOS SIMULADOS</span>', unsafe_allow_html=True)


def render_loaded_badge() -> None:
    st.markdown('<span class="real-badge">🟢 DATOS CARGADOS POR EL USUARIO</span>', unsafe_allow_html=True)


init_state()

# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("Navegación")
    page = st.radio("Sección", NAV_ITEMS, label_visibility="collapsed")
    st.divider()
    seed_value = st.number_input("Semilla de simulación", min_value=0, max_value=999999, step=1, key="seed_widget")
    st.session_state["simulation_seed"] = int(seed_value)
    teacher_mode = st.toggle("Modo docente", value=False, help="Muestra parámetros internos y respuestas esperadas de la simulación.")
    st.button("🔄 Reiniciar laboratorio", on_click=reset_lab, use_container_width=True)
    st.button("🧪 Generar nuevo experimento", on_click=new_experiment, use_container_width=True)
    st.caption(f"Mediciones registradas: {len(st.session_state.get('records', []))}")
    if st.session_state.get("records"):
        st.button("Borrar todas las mediciones", on_click=clear_records, use_container_width=True)
    if teacher_mode:
        with st.expander("Panel docente"):
            st.write(f"Seed activo: {st.session_state['simulation_seed']}")
            if "calibration_state" in st.session_state:
                fit = st.session_state["calibration_state"]["fit"]
                st.write(f"m = {float(fit['slope']):.6f}")
                st.write(f"b0 = {float(fit['intercept']):.6f}")
                st.write(f"R² = {float(fit['r2']):.6f}")
            for key, value in st.session_state.items():
                if key.startswith("unknown_state_") and isinstance(value, dict):
                    st.write(f"Concentración real activa: {value.get('true_c', float('nan')):.4f} mg/L")


# -----------------------------------------------------------------------------
# Pages
# -----------------------------------------------------------------------------
if page == "🏠 Inicio":
    render_header(
        "Laboratorio Virtual de Espectrofotometría",
        "Espectrofotometría UV-Visible y Ley de Beer-Lambert | Bioquímica | Medicina / Enfermería",
    )
    safe_image("home_cover.png")
    st.warning("Este simulador complementa el laboratorio experimental; no sustituye la manipulación real del espectrofotómetro, las cubetas, las soluciones ni las buenas prácticas de laboratorio.")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("Propósito")
        st.write("Observar cómo la interacción luz-materia se transforma en transmitancia, absorbancia, espectro y una relación cuantitativa con la concentración.")
    with c2:
        st.subheader("Tres partes de la práctica")
        st.markdown("1. Espectro de absorción.\n2. Curva de calibración.\n3. Muestra desconocida.")
    with c3:
        st.subheader("Ecuación fundamental")
        st.latex(r"A=\varepsilon b c")
        st.write(f"Analito: **azul de metileno** | Solución madre: **{STOCK_CONCENTRATION_MG_L:g} mg/L** | PM: **{PM_METHYLENE_BLUE} g/mol**")
    st.subheader("Esquema instrumental")
    st.code("Fuente de luz → Selector de longitud de onda → Cubeta con muestra → Detector → Absorbancia", language=None)
    st.info("Secuencia de aprendizaje: **observar → predecir → modificar variables → simular → medir → registrar → analizar → interpretar → aplicar → concluir**.")

elif page == "📘 Fundamento teórico":
    render_header("Fundamento teórico", "Conceptos esenciales antes de experimentar.")
    c1, c2 = st.columns([1.1, 1])
    with c1:
        render_theory_content()
    with c2:
        safe_image("theory.png")

elif page == "💡 Luz, transmitancia y absorbancia":
    render_header("Luz, transmitancia y absorbancia", "Explore la relación logarítmica entre intensidad transmitida y absorbancia.")
    st.info("**¿Qué debe comprender el estudiante?** Una pequeña transmitancia puede corresponder a una absorbancia alta porque A depende logarítmicamente de T.")
    controls, visual = st.columns([0.9, 1.4])
    with controls:
        i0 = st.slider("Intensidad incidente I0 (u.a.)", 1.0, 100.0, 100.0, 1.0)
        i = st.slider("Intensidad transmitida I (u.a.)", 0.1, float(i0), min(50.0, float(i0)), 0.1)
        try:
            t = calculate_transmittance(i, i0)
            a = calculate_absorbance(t)
        except ValueError as exc:
            st.error(str(exc))
            st.stop()
        m1, m2, m3 = st.columns(3)
        m1.metric("T", f"{t:.4f}")
        m2.metric("%T", f"{100*t:.2f} %")
        m3.metric("A", f"{a:.4f}")
        st.latex(r"T=\frac{I}{I_0}\qquad A=-\log_{10}(T)")
        if st.button("Registrar medición", key="record_light"):
            add_record("Luz/T/A", "Actual", {"I0 (u.a.)": i0, "I (u.a.)": i, "T": t, "%T": 100*t, "A": a})
            st.success("Medición registrada.")
    with visual:
        safe_image("light_transmittance_absorbance.png")
        fig_light = go.Figure()
        fig_light.add_trace(go.Scatter(x=[0, 1], y=[0, 0], mode="lines", line=dict(width=max(3, i0 / 8)), name=f"Incidente I0={i0:.1f}"))
        fig_light.add_trace(go.Scatter(x=[1, 2], y=[0, 0], mode="lines", line=dict(width=max(2, i / 8)), name=f"Transmitida I={i:.1f}"))
        fig_light.add_trace(go.Scatter(x=[1], y=[0], mode="markers", marker=dict(size=28, symbol="square-open"), name="Muestra"))
        fig_light.update_layout(title="Representación relativa de intensidades", xaxis=dict(visible=False), yaxis=dict(visible=False, range=[-1, 1]), template="plotly_white", height=260)
        st.plotly_chart(fig_light, use_container_width=True)
    ref = pd.DataFrame({"T": [1.00, 0.50, 0.10, 0.01]})
    ref["%T"] = 100 * ref["T"]
    ref["A"] = -np.log10(ref["T"])
    left, right = st.columns([0.8, 1.2])
    with left:
        st.dataframe(ref, hide_index=True, use_container_width=True)
    with right:
        t_grid = np.linspace(0.01, 1.0, 300)
        fig = go.Figure(go.Scatter(x=t_grid, y=-np.log10(t_grid), mode="lines"))
        fig.update_layout(title="Relación transmitancia–absorbancia", xaxis_title="Transmitancia (T)", yaxis_title="Absorbancia (A)", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

elif page == "🌈 Espectro de absorción":
    render_header("Espectro de absorción", "Barrido virtual de 440 a 800 nm en incrementos de 15 nm.")
    render_simulated_badge()
    st.caption("Datos simulados con fines educativos. El λmax obtenido aquí no debe interpretarse como un resultado experimental real de la práctica.")
    c1, c2 = st.columns([0.85, 1.6])
    with c1:
        lambda0 = st.slider("Posición nominal del máximo λ0 (nm)", 440, 800, 575, 5)
        amplitude = st.slider("Amplitud Amax simulada", 0.1, 2.0, 1.0, 0.05)
        sigma = st.slider("Ancho de banda σ (nm)", 10, 100, 35, 5)
        use_noise = st.checkbox("Activar ruido instrumental", value=False)
        noise_sd = st.slider("Desviación del ruido (A)", 0.0, 0.08, 0.01, 0.005, disabled=not use_noise)
        spectrum_df = generate_spectrum(lambda0, amplitude, sigma, noise_sd if use_noise else 0.0, int(st.session_state["simulation_seed"]))
        lmax, amax = find_lambda_max(spectrum_df)
        st.metric("λmax identificado", f"{lmax:.0f} nm")
        st.metric("Amax", f"{amax:.3f}")
        st.session_state["spectrum_state"] = {"lambda_max_nm": lmax, "amax": amax, "data": spectrum_df}
        if st.button("Registrar medición", key="record_spectrum"):
            add_record("Espectro", "Simulación", {"λmax (nm)": lmax, "Amax": amax, "λ0 nominal (nm)": lambda0, "σ (nm)": sigma})
            st.success("Medición registrada.")
    with c2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=spectrum_df["Wavelength"], y=spectrum_df["Absorbance"], mode="lines+markers", name="Espectro simulado"))
        fig.add_trace(go.Scatter(x=[lmax], y=[amax], mode="markers", marker=dict(size=13), name="λmax"))
        fig.add_vline(x=lmax, line_dash="dash", annotation_text=f"λmax={lmax:.0f} nm")
        fig.update_layout(title="Absorbancia vs longitud de onda", xaxis_title="Longitud de onda (nm)", yaxis_title="Absorbancia", template="plotly_white", height=520)
        st.plotly_chart(fig, use_container_width=True)
    st.download_button("Descargar espectro simulado (CSV)", spectrum_df.to_csv(index=False).encode("utf-8"), "espectro_simulado.csv", "text/csv")
    st.info("λmax corresponde a la longitud de onda donde la sustancia presenta la mayor absorbancia bajo las condiciones evaluadas. El objetivo no es solo encontrar un máximo, sino comprender que la sensibilidad depende de la longitud de onda utilizada.")

    with st.expander("Usar mis datos: espectro CSV/XLSX"):
        uploaded = st.file_uploader("Cargue archivo de espectro", type=["csv", "xlsx", "xls"], key="spectrum_uploader")
        if uploaded is not None:
            try:
                raw = read_uploaded_table(uploaded)
                cols = list(raw.columns)
                wc = st.selectbox("Columna de longitud de onda", cols, index=suggest_column(cols, ("wave", "lambda", "longitud"), 0))
                ac = st.selectbox("Columna de absorbancia", cols, index=suggest_column(cols, ("abs",), 1 if len(cols) > 1 else 0))
                real_df = normalize_spectrum_columns(raw, wc, ac)
                real_lmax, real_amax = find_lambda_max(real_df)
                render_loaded_badge()
                st.metric("λmax en datos cargados", f"{real_lmax:.3f} nm")
                st.metric("Amax", f"{real_amax:.4f}")
                fig_real = go.Figure(go.Scatter(x=real_df["Wavelength"], y=real_df["Absorbance"], mode="lines+markers", name="Datos cargados"))
                fig_real.add_vline(x=real_lmax, line_dash="dash")
                fig_real.update_layout(xaxis_title="Longitud de onda", yaxis_title="Absorbancia", template="plotly_white")
                st.plotly_chart(fig_real, use_container_width=True)
            except Exception as exc:
                st.error(f"No se pudieron analizar los datos: {exc}")

elif page == "🧪 Preparación de soluciones":
    render_header("Preparación de soluciones", "Diluciones de la solución madre de azul de metileno (10 mg/L).")
    st.info("**¿Qué debe comprender el estudiante?** La concentración final depende del volumen de solución madre transferido y del volumen final, no solo del volumen de agua añadido.")
    c1, c2 = st.columns([1.1, 1])
    with c1:
        vstock = np.arange(0, 6, dtype=float)
        water = FINAL_VOLUME_ML - vstock
        conc = STOCK_CONCENTRATION_MG_L * vstock / FINAL_VOLUME_ML
        molar = np.array([mgL_to_molar(c) for c in conc])
        dilutions = pd.DataFrame({
            "Tubo": ["Blanco", "Tubo 1", "Tubo 2", "Tubo 3", "Tubo 4", "Tubo 5"],
            "V solución madre (mL)": vstock,
            "V agua (mL)": water,
            "V final (mL)": FINAL_VOLUME_ML,
            "Concentración (mg/L)": conc,
            "Concentración (mol/L)": molar,
            "Concentración (µmol/L)": molar * 1e6,
        })
        st.dataframe(dilutions, hide_index=True, use_container_width=True)
        st.download_button("Descargar tabla (CSV)", dilutions.to_csv(index=False).encode("utf-8"), "diluciones_azul_metileno.csv", "text/csv")
        st.download_button("Descargar tabla (Excel)", dataframe_to_excel_bytes(dilutions, "Diluciones"), "diluciones_azul_metileno.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with c2:
        safe_image("solution_preparation.png")

    st.subheader("Calculadora general de diluciones")
    u1, u2, u3, u4 = st.columns(4)
    with u1:
        unit = st.selectbox("Unidad de concentración", ["mg/L", "g/L", "mol/L", "mM", "µM"])
    with u2:
        c1_val = st.number_input(f"C1 ({unit})", min_value=0.0, value=10.0 if unit == "mg/L" else 1.0, step=0.1)
    with u3:
        v1_val = st.number_input("V1 alícuota (mL)", min_value=0.0, value=1.0, step=0.1)
    with u4:
        v2_val = st.number_input("V2 volumen final (mL)", min_value=0.01, value=5.0, step=0.1)
    try:
        c2_val = calculate_dilution(c1_val, v1_val, v2_val)
        st.metric(f"C2 ({unit})", f"{c2_val:.6g}")
        st.latex(r"C_1V_1=C_2V_2\quad\Rightarrow\quad C_2=\frac{C_1V_1}{V_2}")
        if st.button("Registrar medición", key="record_dilution"):
            add_record("Dilución", "Calculadora", {f"C1 ({unit})": c1_val, "V1 (mL)": v1_val, "V2 final (mL)": v2_val, f"C2 ({unit})": c2_val})
            st.success("Medición registrada.")
    except ValueError as exc:
        st.error(str(exc))

elif page == "📈 Ley de Beer-Lambert":
    render_header("Ley de Beer-Lambert", "Modifique ε, b y c y observe cómo cambia la absorbancia.")
    st.info("**¿Qué debe comprender el estudiante?** Bajo condiciones ideales, A es directamente proporcional a la concentración y al camino óptico.")
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("Duplicar concentración"):
            st.session_state["bl_c_um"] = min(float(st.session_state["bl_c_um"]) * 2.0, 100.0)
            st.rerun()
    with b2:
        if st.button("Duplicar camino óptico"):
            st.session_state["bl_b"] = min(float(st.session_state["bl_b"]) * 2.0, 2.0)
            st.rerun()
    with b3:
        if st.button("Aumentar absortividad"):
            st.session_state["bl_epsilon"] = min(int(float(st.session_state["bl_epsilon"]) * 1.5), 100000)
            st.rerun()

    controls, graph = st.columns([0.85, 1.45])
    with controls:
        epsilon = st.slider("ε (L mol⁻¹ cm⁻¹)", 1000, 100000, int(st.session_state["bl_epsilon"]), 1000, key="bl_epsilon")
        path = st.slider("b (cm)", 0.1, 2.0, float(st.session_state["bl_b"]), 0.1, key="bl_b")
        c_um = st.slider("c (µmol/L)", 0.0, 100.0, float(st.session_state["bl_c_um"]), 1.0, key="bl_c_um")
        c_molar = c_um * 1e-6
        a = beer_lambert(epsilon, path, c_molar)
        st.metric("Absorbancia A", f"{a:.4f}")
        st.latex(r"A=\varepsilon b c")
        if st.button("Registrar medición", key="record_bl"):
            add_record("Beer-Lambert", "Actual", {"ε (L mol-1 cm-1)": epsilon, "b (cm)": path, "c (µM)": c_um, "A": a})
            st.success("Medición registrada.")
    with graph:
        safe_image("beer_lambert_sliders.png")
        c_grid_um = np.linspace(0, 100, 201)
        a_grid = epsilon * path * c_grid_um * 1e-6
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=c_grid_um, y=a_grid, mode="lines", name="A = εbc"))
        fig.add_trace(go.Scatter(x=[c_um], y=[a], mode="markers", marker=dict(size=13), name="Condición actual"))
        fig.update_layout(title="Concentración vs absorbancia", xaxis_title="Concentración (µmol/L)", yaxis_title="Absorbancia", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("**Pregunta de reflexión:** si ε y b permanecen constantes, ¿qué espera que ocurra con A al duplicar c? Compruébelo con el botón.")

elif page == "📊 Curva de calibración":
    render_header("Curva de calibración", "Construya A = mC + b0, evalúe residuos y estime absortividad molar.")
    safe_image("calibration_curve.png")
    source = st.radio("Fuente de datos", ["Simulación", "Usar mis datos"], horizontal=True)

    if source == "Simulación":
        render_simulated_badge()
        st.caption("La pendiente, el intercepto, R² y las absorbancias generadas son valores sintéticos. No se presentan como resultados experimentales de la práctica.")
        mode = st.selectbox("Modo", ["Ideal", "Experimental"])
        p1, p2 = st.columns(2)
        with p1:
            sim_slope = st.number_input("Pendiente simulada (Abs por mg/L)", min_value=0.001, max_value=0.5, value=0.095, step=0.005, format="%.3f")
        with p2:
            sim_intercept = st.number_input("Intercepto simulado b0 (A)", min_value=-0.1, max_value=0.2, value=0.010, step=0.005, format="%.3f")
        config = ErrorConfig()
        if mode == "Experimental":
            st.markdown("**Seleccione fuentes de variación para esta simulación:**")
            e1, e2, e3, e4 = st.columns(4)
            with e1:
                instrument_noise = st.checkbox("Ruido instrumental", value=True, key="cal_noise")
                pipetting = st.checkbox("Error de pipeteo", value=False, key="cal_pip")
            with e2:
                fingerprints = st.checkbox("Cubeta con huellas", value=False, key="cal_fp")
                bubble = st.checkbox("Burbuja", value=False, key="cal_bubble")
            with e3:
                wrong_blank = st.checkbox("Blanco incorrecto", value=False, key="cal_blank")
                stray = st.checkbox("Luz parásita", value=False, key="cal_stray")
            with e4:
                nonlinear = st.checkbox("Pérdida de linealidad", value=False, key="cal_nonlin")
                noise_sd = st.slider("σ ruido (A)", 0.0, 0.08, 0.012, 0.002, key="cal_noise_sd")
            config = ErrorConfig(
                instrument_noise=instrument_noise,
                pipetting_error=pipetting,
                fingerprints=fingerprints,
                bubble=bubble,
                wrong_blank=wrong_blank,
                stray_light=stray,
                high_concentration_nonlinearity=nonlinear,
                noise_sd=noise_sd,
            )
        cal_df = generate_calibration_data(
            DEFAULT_CALIBRATION_CONCENTRATIONS_MG_L,
            sim_slope,
            sim_intercept,
            mode,
            config,
            int(st.session_state["simulation_seed"]),
        )
        x_col, y_col = "Concentration_nominal_mg_L", "Absorbance"
        fit = fit_calibration_curve(cal_df, x_col, y_col)
        st.session_state["calibration_state"] = {"data": cal_df, "fit": fit, "source": "SIMULACIÓN", "x_col": x_col, "y_col": y_col}
    else:
        uploaded = st.file_uploader("Cargue curva de calibración CSV/XLSX", type=["csv", "xlsx", "xls"], key="cal_uploader")
        if uploaded is None:
            st.info("Formato esperado: una columna de concentración y una de absorbancia.")
            st.stop()
        try:
            raw = read_uploaded_table(uploaded)
            cols = list(raw.columns)
            conc_col = st.selectbox("Columna de concentración", cols, index=suggest_column(cols, ("conc",), 0))
            abs_col = st.selectbox("Columna de absorbancia", cols, index=suggest_column(cols, ("abs",), 1 if len(cols) > 1 else 0))
            cal_df = normalize_calibration_columns(raw, conc_col, abs_col)
            x_col, y_col = "Concentration", "Absorbance"
            fit = fit_calibration_curve(cal_df, x_col, y_col)
            render_loaded_badge()
            st.session_state["calibration_state"] = {"data": cal_df, "fit": fit, "source": "USUARIO", "x_col": x_col, "y_col": y_col}
        except Exception as exc:
            st.error(f"No se pudieron analizar los datos: {exc}")
            st.stop()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Pendiente m", f"{float(fit['slope']):.6f}")
    m2.metric("Intercepto b0", f"{float(fit['intercept']):.6f}")
    m3.metric("R²", f"{float(fit['r2']):.5f}")
    m4.metric("n", f"{int(fit['n'])}")
    st.latex(r"A=mc+b_0")
    st.write(f"**Ecuación ajustada:** A = {float(fit['slope']):.6f}·C + ({float(fit['intercept']):.6f})")
    st.plotly_chart(calibration_plot(cal_df, x_col, y_col, fit, "Curva de calibración"), use_container_width=True)
    st.dataframe(cal_df, hide_index=True, use_container_width=True)
    d1, d2 = st.columns(2)
    with d1:
        st.download_button("Descargar calibración (CSV)", cal_df.to_csv(index=False).encode("utf-8"), "calibracion_espectrofotometria.csv", "text/csv")
    with d2:
        st.download_button("Descargar calibración (Excel)", dataframe_to_excel_bytes(cal_df, "Calibracion"), "calibracion_espectrofotometria.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with st.expander("Análisis avanzado: residuos"):
        residual_df = pd.DataFrame({"Concentración": fit["x"], "Residuo": fit["residuals"]})
        fig_res = go.Figure(go.Scatter(x=residual_df["Concentración"], y=residual_df["Residuo"], mode="markers"))
        fig_res.add_hline(y=0, line_dash="dash")
        fig_res.update_layout(title="Residuos vs concentración", xaxis_title="Concentración (mg/L)", yaxis_title="Residuo de absorbancia", template="plotly_white")
        st.plotly_chart(fig_res, use_container_width=True)
        st.caption("Una distribución aparentemente aleatoria alrededor de cero es compatible con el comportamiento esperado de un modelo lineal. Un R² alto, por sí solo, no demuestra que el modelo sea perfecto.")

    with st.expander("Absortividad molar"):
        path_cm = st.slider("Longitud de cubeta b (cm)", 0.1, 2.0, 1.0, 0.1, key="epsilon_path")
        eps_result = molar_absorptivity_from_calibration(np.asarray(fit["x"], dtype=float), np.asarray(fit["y"], dtype=float), path_cm, PM_METHYLENE_BLUE)
        st.metric("ε estimada", f"{eps_result['epsilon_l_mol_cm']:.3e} L mol⁻¹ cm⁻¹")
        st.write(f"Regresión A vs mol/L: R² = {eps_result['r2']:.5f}")
        st.caption("Para datos simulados, ε es igualmente un resultado simulado. Para datos cargados por el usuario, el cálculo depende de que la concentración X esté expresada en mg/L de azul de metileno.")

    if st.button("Registrar medición", key="record_calibration"):
        add_record("Calibración", st.session_state["calibration_state"]["source"], {"m": fit["slope"], "b0": fit["intercept"], "R²": fit["r2"], "n": fit["n"]})
        st.success("Medición registrada.")
    st.info("**¿Qué debe comprender el estudiante?** La curva de calibración relaciona una señal instrumental con concentraciones conocidas para estimar posteriormente una muestra desconocida.")

elif page == "❓ Muestra desconocida":
    render_header("Muestra desconocida", "Utilice la ecuación de calibración completa: c = (A - b0)/m.")
    safe_image("unknown_sample.png")
    state = default_calibration_state()
    fit = state["fit"]
    render_simulated_badge()
    challenge = st.radio("Tipo de reto", ["Interpolación", "Extrapolación"], horizontal=True)
    state_key = f"unknown_state_{challenge}_{st.session_state['simulation_seed']}_{st.session_state['unknown_counter']}"
    if state_key not in st.session_state:
        seed = int(st.session_state["simulation_seed"]) + 1000 + int(st.session_state["unknown_counter"])
        true_c = generate_unknown_concentration(seed, challenge)
        unknown_a = simulate_unknown_absorbance(true_c, float(fit["slope"]), float(fit["intercept"]), seed + 1)
        st.session_state[state_key] = {"true_c": true_c, "absorbance": unknown_a}
        st.session_state["unknown_revealed"] = False
    unknown_state = st.session_state[state_key]

    if st.button("Generar nueva muestra desconocida"):
        st.session_state["unknown_counter"] += 1
        st.session_state["unknown_revealed"] = False
        st.rerun()

    st.metric("Absorbancia de la muestra", f"{unknown_state['absorbance']:.4f}")
    student_guess = st.number_input("Antes de revelar: estime la concentración (mg/L)", min_value=0.0, max_value=25.0, value=5.0, step=0.1)
    st.latex(r"c=\frac{A-b_0}{m}")
    if challenge == "Interpolación":
        st.success("La muestra fue generada para practicar interpolación dentro del rango 0–10 mg/L.")
    else:
        st.warning("Esta actividad practica extrapolación. Una estimación fuera del rango de calibración puede presentar mayor incertidumbre; en un laboratorio real, considere diluir la muestra y repetir la medición.")

    if st.button("Revelar concentración real"):
        st.session_state["unknown_revealed"] = True
    if st.session_state.get("unknown_revealed", False):
        result = evaluate_unknown(float(unknown_state["absorbance"]), float(fit["slope"]), float(fit["intercept"]), float(unknown_state["true_c"]))
        g1, g2, g3, g4 = st.columns(4)
        g1.metric("Concentración estimada", f"{result['estimated_concentration_mg_l']:.4f} mg/L")
        g2.metric("Concentración real", f"{result['true_concentration_mg_l']:.4f} mg/L")
        g3.metric("Error absoluto", f"{result['absolute_error_mg_l']:.4f} mg/L")
        g4.metric("Error porcentual", f"{result['percentage_error']:.2f} %")
        student_error = abs(student_guess - result["true_concentration_mg_l"])
        st.write(f"Su estimación previa difirió en **{student_error:.4f} mg/L** del valor real simulado.")
        st.session_state["last_unknown_result"] = result | {"absorbance": unknown_state["absorbance"], "challenge": challenge}
        cal_df = state["data"]
        x_col, y_col = state["x_col"], state["y_col"]
        fig = calibration_plot(cal_df, x_col, y_col, fit, "Ubicación de la muestra desconocida")
        fig.add_trace(go.Scatter(x=[result["estimated_concentration_mg_l"]], y=[unknown_state["absorbance"]], mode="markers", marker=dict(size=14, symbol="diamond"), name="Muestra desconocida"))
        fig.add_hline(y=unknown_state["absorbance"], line_dash="dot")
        fig.add_vline(x=result["estimated_concentration_mg_l"], line_dash="dot")
        st.plotly_chart(fig, use_container_width=True)
        if st.button("Registrar medición", key="record_unknown"):
            add_record("Muestra desconocida", challenge, {"A muestra": unknown_state["absorbance"], "C estimada (mg/L)": result["estimated_concentration_mg_l"], "C real (mg/L)": result["true_concentration_mg_l"], "Error (%)": result["percentage_error"]})
            st.success("Medición registrada.")

elif page == "⚠️ Errores experimentales":
    render_header("Errores experimentales", "Compare Beer-Lambert ideal con datos simulados afectados por errores comunes.")
    st.info("**¿Qué debe comprender el estudiante?** Un error puede cambiar pendiente, intercepto, dispersión o linealidad. Identificar el patrón es parte del análisis, no solo observar un R².")
    img1, img2 = st.columns(2)
    with img1:
        safe_image("errors_overview.png")
    with img2:
        safe_image("cuvette_handling.png")

    st.subheader("Active errores de forma independiente")
    c1, c2, c3 = st.columns(3)
    with c1:
        e_noise = st.checkbox("Ruido instrumental", key="err_noise")
        st.caption("Añade pequeñas fluctuaciones aleatorias a las lecturas.")
        e_pip = st.checkbox("Error de pipeteo", key="err_pip")
        st.caption("La concentración realmente preparada difiere ligeramente de la nominal.")
        e_fp = st.checkbox("Cubeta con huellas", key="err_fp")
        st.caption("Introduce atenuación adicional aproximadamente sistemática.")
    with c2:
        e_bubble = st.checkbox("Burbuja", key="err_bubble")
        st.caption("Aumenta la variabilidad de una lectura.")
        e_blank = st.checkbox("Blanco incorrecto", key="err_blank")
        st.caption("Desplaza la línea base y modifica el intercepto.")
    with c3:
        e_stray = st.checkbox("Luz parásita", key="err_stray")
        st.caption("Comprime absorbancias altas y puede generar desviación de linealidad.")
        e_nonlin = st.checkbox("Concentración elevada / pérdida de linealidad", key="err_nonlin")
        st.caption("Introduce una desviación descendente a concentraciones altas.")
    err_noise_sd = st.slider("Nivel de ruido σ (A)", 0.0, 0.08, 0.015, 0.002)

    ideal_df = generate_calibration_data(mode="Ideal", seed=int(st.session_state["simulation_seed"]))
    err_cfg = ErrorConfig(
        instrument_noise=e_noise,
        pipetting_error=e_pip,
        fingerprints=e_fp,
        bubble=e_bubble,
        wrong_blank=e_blank,
        stray_light=e_stray,
        high_concentration_nonlinearity=e_nonlin,
        noise_sd=err_noise_sd,
    )
    exp_df = generate_calibration_data(mode="Experimental", error_config=err_cfg, seed=int(st.session_state["simulation_seed"]))
    fit_i = fit_calibration_curve(ideal_df, "Concentration_nominal_mg_L", "Absorbance")
    fit_e = fit_calibration_curve(exp_df, "Concentration_nominal_mg_L", "Absorbance")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ideal_df["Concentration_nominal_mg_L"], y=ideal_df["Absorbance"], mode="lines+markers", name="Ideal"))
    fig.add_trace(go.Scatter(x=exp_df["Concentration_nominal_mg_L"], y=exp_df["Absorbance"], mode="markers", name="Experimental simulado"))
    x_line = np.linspace(0, 10, 200)
    fig.add_trace(go.Scatter(x=x_line, y=float(fit_e["slope"])*x_line+float(fit_e["intercept"]), mode="lines", name="Regresión experimental"))
    fig.update_layout(title="Ideal vs experimental simulado", xaxis_title="Concentración (mg/L)", yaxis_title="Absorbancia", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)
    compare = pd.DataFrame({
        "Parámetro": ["Pendiente m", "Intercepto b0", "R²"],
        "Ideal": [fit_i["slope"], fit_i["intercept"], fit_i["r2"]],
        "Experimental simulado": [fit_e["slope"], fit_e["intercept"], fit_e["r2"]],
    })
    st.dataframe(compare, hide_index=True, use_container_width=True)
    with st.expander("Camino óptico y concentración"):
        safe_image("optical_path_comparison.png")
    if st.button("Registrar medición", key="record_errors"):
        add_record("Errores", err_cfg.__repr__(), {"m experimental": fit_e["slope"], "b0 experimental": fit_e["intercept"], "R² experimental": fit_e["r2"]})
        st.success("Medición registrada.")

elif page == "🎯 Laboratorio virtual completo":
    render_header("Laboratorio virtual completo", "Modo guiado con progreso, registro experimental y reporte final.")
    st.button("Generar nuevo experimento", on_click=new_experiment, key="guided_new_experiment")
    steps = [
        "Encender espectrofotómetro y reconocer que la estabilización real requiere tiempo (15–20 min; aquí no se espera).",
        "Preparar el blanco con agua destilada.",
        "Realizar barrido espectral de 440–800 nm.",
        "Determinar λmax.",
        "Preparar estándares de 0–10 mg/L.",
        "Medir absorbancias de los estándares.",
        "Construir la curva de calibración.",
        "Calcular regresión lineal A = mC + b0.",
        "Medir la muestra desconocida.",
        "Determinar la concentración con c = (A-b0)/m.",
        "Calcular el error cuando se revele la concentración real simulada.",
        "Interpretar resultados, limitaciones y posibles fuentes de error.",
    ]
    completed = 0
    for i, step in enumerate(steps, start=1):
        checked = st.checkbox(f"Paso {i}. {step}", key=f"lab_step_{i}")
        completed += int(checked)
    st.progress(completed / len(steps), text=f"Progreso: {completed}/{len(steps)} pasos")
    st.info("Use las secciones del menú para realizar cada etapa. Después de cada condición relevante pulse **Registrar medición**.")

    st.subheader("Registro experimental acumulado")
    rec_df = records_dataframe()
    if rec_df.empty:
        st.info("Aún no hay mediciones registradas.")
    else:
        st.dataframe(rec_df, hide_index=True, use_container_width=True)
        r1, r2 = st.columns(2)
        with r1:
            st.download_button("Descargar registros (CSV)", rec_df.to_csv(index=False).encode("utf-8"), "experimentos_espectrofotometria.csv", "text/csv")
        with r2:
            st.download_button("Descargar registros (Excel)", dataframe_to_excel_bytes(rec_df, "Experimentos"), "experimentos_espectrofotometria.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.subheader("Reporte final")
    spectrum_state = st.session_state.get("spectrum_state", {})
    cal_state = st.session_state.get("calibration_state", {})
    unk = st.session_state.get("last_unknown_result", {})
    fit = cal_state.get("fit", {}) if isinstance(cal_state, dict) else {}
    summary = pd.DataFrame(
        {
            "Resultado": ["λmax determinada", "Amax", "Pendiente m", "Intercepto b0", "R²", "Absorbancia muestra", "Concentración estimada", "Concentración real revelada", "Error porcentual"],
            "Valor": [
                spectrum_state.get("lambda_max_nm", "Pendiente"),
                spectrum_state.get("amax", "Pendiente"),
                fit.get("slope", "Pendiente") if fit else "Pendiente",
                fit.get("intercept", "Pendiente") if fit else "Pendiente",
                fit.get("r2", "Pendiente") if fit else "Pendiente",
                unk.get("absorbance", "Pendiente"),
                unk.get("estimated_concentration_mg_l", "Pendiente"),
                unk.get("true_concentration_mg_l", "Pendiente"),
                unk.get("percentage_error", "Pendiente"),
            ],
            "Unidad/nota": ["nm", "A", "A/(mg/L)", "A", "", "A", "mg/L", "mg/L", "%"],
        }
    )
    st.dataframe(summary, hide_index=True, use_container_width=True)
    h1, h2 = st.columns(2)
    with h1:
        st.download_button("Descargar resumen (CSV)", summary.to_csv(index=False).encode("utf-8"), "reporte_final_espectrofotometria.csv", "text/csv")
    with h2:
        report_html = build_html_report("Reporte final - Laboratorio Virtual de Espectrofotometría", summary, rec_df)
        st.download_button("Descargar reporte (HTML)", report_html.encode("utf-8"), "reporte_final_espectrofotometria.html", "text/html")

elif page == "📝 Autoevaluación":
    render_header("Autoevaluación", "Compruebe comprensión conceptual, cuantitativa e interpretativa.")
    render_quiz()
    st.divider()
    st.subheader("Actividad de interpretación")
    st.write("Una muestra presenta una absorbancia mayor que el estándar más concentrado. ¿Qué haría antes de reportar el resultado?")
    interpretation = st.radio("Seleccione una opción", ["Extrapolar sin restricciones", "Diluir la muestra y repetir", "Cambiar arbitrariamente el intercepto", "Ignorar el dato"], index=None, key="interpret_case")
    if st.button("Revisar caso"):
        if interpretation == "Diluir la muestra y repetir":
            st.success("Adecuado. Diluir permite regresar al intervalo cubierto por la calibración y reducir el riesgo asociado a la extrapolación.")
        else:
            st.warning("Revise el concepto de rango de calibración e interpolación/extrapolación.")
    st.divider()
    render_lab_questionnaire()

elif page == "📚 Conceptos clave":
    render_header("Conceptos clave", "Glosario y preguntas de reflexión para cerrar la práctica.")
    render_key_concepts()
    st.subheader("Preguntas de reflexión")
    st.markdown(
        "- ¿Qué ocurriría con A si duplicamos c manteniendo ε y b constantes?\n"
        "- ¿Por qué conviene realizar mediciones cuantitativas cerca de λmax?\n"
        "- ¿Qué efecto puede tener una burbuja en la cubeta?\n"
        "- ¿Por qué el blanco debe medirse antes de las muestras?\n"
        "- ¿Por qué no conviene extrapolar fuera del intervalo de calibración?"
    )
    st.subheader("Limitaciones científicas")
    st.write("El modelo ideal A = εbc puede desviarse por altas concentraciones, luz parásita, dispersión/turbidez, interacciones moleculares, cambios químicos del analito, errores de preparación y características instrumentales.")

# Footer shared by all pages
st.divider()
st.caption("Laboratorio Virtual de Espectrofotometría | Azul de metileno: 10 mg/L (solución madre), PM = 319.8 g/mol | Los valores sintéticos están identificados como simulación.")
