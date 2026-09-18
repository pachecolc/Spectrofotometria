"""Short pedagogical theory blocks for the Streamlit interface."""
from __future__ import annotations

import streamlit as st


def render_theory_content() -> None:
    st.info("**¿Qué debe comprender el estudiante?** La espectrofotometría relaciona la interacción entre luz y materia con una señal cuantitativa que puede usarse para estimar concentración.")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Radiación electromagnética")
        st.markdown(
            "La luz puede describirse por su **longitud de onda (λ)**, frecuencia y energía. "
            "En espectrofotometría UV-Visible se selecciona una región de λ y se mide cuánta radiación atraviesa la muestra."
        )
        st.latex(r"c = \lambda\nu")
        st.latex(r"E = h\nu")
        st.subheader("Interacción luz-materia")
        st.markdown(
            "Un **cromóforo** absorbe ciertas longitudes de onda cuando la energía de la radiación coincide con transiciones electrónicas permitidas. "
            "La absorción selectiva produce un espectro característico."
        )
    with c2:
        st.subheader("Transmitancia y absorbancia")
        st.latex(r"T=\frac{I}{I_0}")
        st.latex(r"\%T=100\frac{I}{I_0}")
        st.latex(r"A=-\log_{10}(T)=\log_{10}\left(\frac{I_0}{I}\right)")
        st.markdown(
            "La transmitancia expresa la fracción de luz que atraviesa la muestra. La absorbancia aumenta cuando la muestra transmite menos luz."
        )
        st.subheader("Ley de Beer-Lambert")
        st.latex(r"A=\varepsilon b c")
        st.markdown(
            "Bajo condiciones ideales, la absorbancia es proporcional a la absortividad molar (ε), la longitud del trayecto óptico (b) y la concentración (c)."
        )

    with st.expander("Supuestos y limitaciones del modelo"):
        st.markdown(
            "- radiación suficientemente monocromática;\n"
            "- muestra homogénea y sin dispersión importante;\n"
            "- ausencia de cambios químicos relevantes del analito;\n"
            "- respuesta instrumental dentro de su intervalo útil;\n"
            "- concentraciones donde la relación A-c sea aproximadamente lineal.\n\n"
            "A altas concentraciones, con luz parásita, turbidez, errores de preparación u otras limitaciones instrumentales, pueden aparecer desviaciones."
        )


def render_key_concepts() -> None:
    concepts = {
        "Transmitancia (T)": "Fracción de intensidad transmitida respecto a la incidente: I/I0.",
        "Absorbancia (A)": "Medida logarítmica de atenuación de la luz: -log10(T).",
        "λmax": "Longitud de onda donde se observa la mayor absorbancia bajo las condiciones evaluadas.",
        "Cromóforo": "Grupo molecular responsable de absorber radiación en una región del espectro.",
        "Absortividad molar (ε)": "Constante de proporcionalidad de Beer-Lambert, con unidades L mol⁻¹ cm⁻¹.",
        "Trayecto óptico (b)": "Distancia recorrida por la luz dentro de la muestra, usualmente en cm.",
        "Curva de calibración": "Relación entre señales instrumentales y concentraciones conocidas.",
        "Pendiente": "Cambio de absorbancia por unidad de concentración dentro del modelo lineal.",
        "Intercepto (b0)": "Absorbancia predicha cuando la concentración es cero.",
        "R²": "Proporción de variabilidad explicada por el ajuste lineal; no demuestra por sí solo que el modelo sea perfecto.",
        "Interpolación": "Estimación dentro del intervalo cubierto por los estándares.",
        "Extrapolación": "Estimación fuera del intervalo de calibración; suele implicar mayor incertidumbre.",
    }
    st.info("**¿Qué debe comprender el estudiante?** Los términos de la técnica describen partes diferentes del proceso experimental y del modelo matemático.")
    for term, definition in concepts.items():
        with st.expander(term):
            st.write(definition)
