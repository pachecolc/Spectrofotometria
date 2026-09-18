"""Self-assessment and laboratory questionnaire."""
from __future__ import annotations

import streamlit as st

QUESTIONS = [
    {
        "question": "Si T = 0.10, ¿cuál es la absorbancia?",
        "options": ["0.10", "0.301", "1.00", "10.0"],
        "answer": "1.00",
        "feedback": "A = -log10(0.10) = 1.00.",
    },
    {
        "question": "Cuando I = I0, la absorbancia es:",
        "options": ["0", "1", "100", "No puede calcularse"],
        "answer": "0",
        "feedback": "Si I = I0, T = 1 y A = -log10(1) = 0.",
    },
    {
        "question": "λmax corresponde a:",
        "options": ["La menor transmitancia posible del equipo", "La longitud de onda de mayor absorbancia observada", "La concentración máxima", "El intercepto de calibración"],
        "answer": "La longitud de onda de mayor absorbancia observada",
        "feedback": "λmax es la longitud de onda donde la sustancia presenta la mayor absorbancia bajo las condiciones evaluadas.",
    },
    {
        "question": "Bajo condiciones ideales de Beer-Lambert, si se duplica c y ε y b permanecen constantes, A:",
        "options": ["Se reduce a la mitad", "No cambia", "Se duplica", "Se hace cero"],
        "answer": "Se duplica",
        "feedback": "A = εbc, por lo que A es proporcional a c.",
    },
    {
        "question": "Una solución madre de 10 mg/L se diluye tomando 2 mL y completando a 5 mL. C2 es:",
        "options": ["2 mg/L", "4 mg/L", "5 mg/L", "20 mg/L"],
        "answer": "4 mg/L",
        "feedback": "C2 = C1·V1/V2 = 10·2/5 = 4 mg/L.",
    },
    {
        "question": "¿Cuál es la función principal de una curva de calibración?",
        "options": ["Eliminar todo error experimental", "Relacionar señal instrumental con concentración conocida", "Cambiar λmax", "Hacer que el intercepto sea cero"],
        "answer": "Relacionar señal instrumental con concentración conocida",
        "feedback": "La calibración permite usar estándares conocidos para estimar una muestra desconocida.",
    },
    {
        "question": "Una muestra estimada dentro del intervalo 0–10 mg/L de los estándares se obtiene por:",
        "options": ["Interpolación", "Extrapolación", "Normalización", "Derivación"],
        "answer": "Interpolación",
        "feedback": "La interpolación ocurre dentro del rango cubierto por los estándares.",
    },
    {
        "question": "¿Qué efecto puede producir la luz parásita a absorbancias altas?",
        "options": ["Desviación de linealidad", "Aumento exacto y proporcional de A", "Conversión de mg/L a mol/L", "Eliminación del ruido"],
        "answer": "Desviación de linealidad",
        "feedback": "La luz parásita puede hacer que las absorbancias altas se subestimen y aparezca curvatura.",
    },
    {
        "question": "El blanco se usa principalmente para:",
        "options": ["Corregir contribuciones del solvente/cubeta y establecer referencia", "Aumentar la concentración", "Determinar el peso molecular", "Sustituir la muestra desconocida"],
        "answer": "Corregir contribuciones del solvente/cubeta y establecer referencia",
        "feedback": "El blanco establece la referencia instrumental de los componentes que no son el analito.",
    },
    {
        "question": "Si la pendiente de A vs concentración molar es m y la cubeta tiene longitud b, la absortividad molar es:",
        "options": ["ε = b/m", "ε = m/b", "ε = m·b", "ε = 1/(m·b)"],
        "answer": "ε = m/b",
        "feedback": "De A = εbc, la pendiente respecto a c es m = εb; por tanto ε = m/b.",
    },
]

LAB_QUESTIONNAIRE = [
    ("Interpretar la gráfica longitud de onda vs absorbancia.", "Describa la tendencia general, el máximo observado y cómo cambia la absorbancia a ambos lados del máximo."),
    ("Identificar el pico de mayor absorbancia.", "Informe λmax y Amax a partir de sus propios datos simulados o cargados."),
    ("Calcular absortividad molar.", "Convierta concentración a mol/L, ajuste A vs c y use ε = m/b."),
    ("Determinar la concentración molar del cromóforo.", "Convierta primero mg/L a g/L y luego divida por 319.8 g/mol."),
    ("Explicar aplicaciones profesionales de la espectrofotometría.", "Relacione la técnica con cuantificación de analitos, seguimiento de reacciones o análisis clínico/bioquímico."),
    ("Explicar qué significa físicamente la absorbancia.", "Relacione A con la atenuación logarítmica de la intensidad transmitida respecto a la incidente."),
    ("Diferenciar absortividad y absortividad molar.", "Indique qué concentración utiliza cada forma y especifique unidades."),
    ("Explicar para qué sirve una curva de calibración.", "Explique cómo estándares conocidos permiten estimar una muestra desconocida."),
    ("Describir limitaciones de la Ley de Beer-Lambert.", "Considere altas concentraciones, luz parásita, dispersión, turbidez, cambios químicos y errores de preparación."),
]


def render_quiz() -> None:
    st.info("Responda primero. La retroalimentación aparece únicamente al enviar el intento.")
    with st.form("quiz_form"):
        answers = {}
        for i, q in enumerate(QUESTIONS, start=1):
            answers[i] = st.radio(f"{i}. {q['question']}", q["options"], index=None, key=f"quiz_q_{i}")
        submitted = st.form_submit_button("Calificar intento")
    if submitted:
        score = 0
        for i, q in enumerate(QUESTIONS, start=1):
            user_answer = answers[i]
            if user_answer == q["answer"]:
                score += 1
                st.success(f"{i}. Correcta. {q['feedback']}")
            else:
                st.error(f"{i}. Revise su respuesta. {q['feedback']}")
        st.metric("Puntaje", f"{score}/{len(QUESTIONS)}")


def render_lab_questionnaire() -> None:
    st.subheader("Cuestionario del laboratorio")
    st.caption("Escriba sus respuestas antes de solicitar orientaciones.")
    for i, (question, _) in enumerate(LAB_QUESTIONNAIRE, start=1):
        st.text_area(f"{i}. {question}", key=f"lab_question_{i}")
    if st.button("Mostrar orientaciones", key="show_lab_guidance"):
        st.session_state["lab_guidance_visible"] = True
    if st.session_state.get("lab_guidance_visible", False):
        for i, (_, guidance) in enumerate(LAB_QUESTIONNAIRE, start=1):
            st.info(f"**Orientación {i}:** {guidance}")
