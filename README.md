# Laboratorio Virtual de Espectrofotometría

Aplicación educativa interactiva en **Python + Streamlit + Plotly** para estudiar espectrofotometría UV-Visible, transmitancia, absorbancia, espectros de absorción, preparación de diluciones, Ley de Beer-Lambert, curvas de calibración y determinación de una muestra desconocida.

La práctica está orientada a estudiantes de primeros semestres de **Medicina, Enfermería y Bioquímica**. El analito definido para esta práctica es **azul de metileno**, con solución madre de **10 mg/L** y peso molecular de **319.8 g/mol**.

> Los valores generados por el programa se identifican como **SIMULACIÓN**. No se presentan absorbancias, λmax, absortividades, pendientes, interceptos o R² simulados como si fueran resultados experimentales reales.

## Objetivo

Integrar teoría, predicción, manipulación de variables, simulación, registro de mediciones, análisis e interpretación para comprender cómo una señal óptica puede relacionarse cuantitativamente con la concentración.

## Características

- Menú lateral con 12 módulos.
- Transmitancia, %T y absorbancia a partir de I e I0.
- Barrido espectral en las longitudes de onda de la práctica: 440–800 nm cada 15 nm.
- Detección automática de λmax en datos simulados o cargados.
- Preparación de estándares 0, 2, 4, 6, 8 y 10 mg/L.
- Conversión mg/L → g/L → mol/L → µmol/L usando PM = 319.8 g/mol.
- Simulador interactivo A = εbc.
- Curva de calibración ideal o experimental simulada.
- Regresión A = mC + b0, R² y análisis de residuos.
- Cálculo de absortividad molar.
- Muestra desconocida con interpolación/extrapolación y error.
- Simulación de ruido, pipeteo, huellas, burbuja, blanco incorrecto, luz parásita y pérdida de linealidad.
- Carga de datos propios CSV/XLSX para espectro o calibración.
- Registro de múltiples mediciones con `st.session_state`.
- Exportación a CSV y Excel.
- Reporte final descargable en CSV y HTML.
- Autoevaluación y cuestionario de laboratorio.
- Modo docente sin contraseña.
- Imágenes educativas en `assets/` con carga segura.

## Fundamento científico

### Transmitancia

```text
T = I / I0
%T = 100 · I/I0
```

### Absorbancia

```text
A = -log10(T) = log10(I0/I)
```

### Ley de Beer-Lambert

```text
A = εbc
```

### Dilución

```text
C1V1 = C2V2
C2 = C1V1/V2
```

### Curva de calibración

```text
A = mC + b0
```

### Muestra desconocida

```text
C = (A - b0)/m
```

No se usa automáticamente `C = A/m` porque el intercepto de una calibración real o simulada puede ser distinto de cero.

## Variables principales

| Variable | Símbolo | Unidad típica | Papel |
|---|---|---|---|
| Intensidad incidente | I0 | u.a. | Entrada |
| Intensidad transmitida | I | u.a. | Entrada |
| Transmitancia | T | adimensional | Salida |
| Absorbancia | A | adimensional | Salida |
| Longitud de onda | λ | nm | Independiente |
| Concentración | c | mg/L, mol/L, µM | Independiente |
| Absortividad molar | ε | L mol⁻¹ cm⁻¹ | Parámetro |
| Camino óptico | b | cm | Parámetro |

## Instalación

Se recomienda Python 3.11 o 3.12.

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

## Ejecución local

Desde la carpeta del proyecto:

```bash
streamlit run app.py
```

## Estructura del proyecto

```text
spectrophotometry_lab/
├── app.py
├── requirements.txt
├── README.md
├── GUIA_LABORATORIO.md
├── LICENSE
├── .gitignore
├── smoke_test.py
├── modules/
│   ├── __init__.py
│   ├── theory.py
│   ├── calculations.py
│   ├── spectrum.py
│   ├── calibration.py
│   ├── simulation.py
│   ├── unknown.py
│   ├── errors.py
│   └── quiz.py
├── data/
│   └── example_data.csv
└── assets/
    ├── README.md
    ├── home_cover.png
    ├── theory.png
    ├── light_transmittance_absorbance.png
    ├── absorption_spectrum.png
    ├── solution_preparation.png
    ├── beer_lambert_sliders.png
    ├── calibration_curve.png
    ├── unknown_sample.png
    ├── errors_overview.png
    ├── cuvette_handling.png
    └── optical_path_comparison.png
```

## Uso para estudiantes

1. Revise **Fundamento teórico**.
2. Prediga qué ocurrirá antes de mover controles.
3. Explore transmitancia y absorbancia.
4. Obtenga un espectro simulado y determine λmax.
5. Revise las diluciones de 0–10 mg/L.
6. Explore A = εbc.
7. Construya una calibración y examine residuos.
8. Resuelva una muestra desconocida.
9. Active errores experimentales y compare el efecto.
10. Pulse **Registrar medición** después de cada condición importante.
11. Descargue CSV/XLSX y complete la guía.

## Usar datos experimentales propios

### Espectro

Columnas esperadas, por ejemplo:

```text
Wavelength,Absorbance
```

### Calibración

Columnas esperadas, por ejemplo:

```text
Concentration,Absorbance
```

La aplicación permite seleccionar manualmente las columnas si los nombres son distintos. Cuando se cargan datos del usuario, no se añade ruido artificial.

## Capturas de pantalla

Añada aquí capturas después del despliegue:

- `docs/inicio.png`
- `docs/espectro.png`
- `docs/calibracion.png`
- `docs/muestra_desconocida.png`

## Despliegue en Streamlit Community Cloud

1. Cree un repositorio nuevo en GitHub.
2. Suba el contenido de esta carpeta a la raíz del repositorio.
3. Verifique que `requirements.txt` esté en la raíz.
4. Entre a Streamlit Community Cloud.
5. Seleccione el repositorio.
6. Configure:

```text
Repository: <su-repositorio>
Branch: main
Main file: app.py
```

7. Pulse **Deploy**.
8. Compruebe que las imágenes de `assets/` estén versionadas en Git.

## Limitaciones del modelo

La Ley de Beer-Lambert supone condiciones ideales. La aplicación representa de forma pedagógica desviaciones por alta concentración, luz parásita, dispersión/turbidez, cambios químicos, errores de preparación y efectos instrumentales, pero no pretende reproducir todos los mecanismos físicos de un espectrofotómetro real.

El espectro gaussiano es un modelo sintético educativo. Su λmax no debe confundirse con un λmax experimental del azul de metileno obtenido en esta práctica.

## Validaciones implementadas

- División por cero.
- T fuera de 0 < T ≤ 1.
- I > I0.
- Concentraciones negativas.
- V1 > V2 en diluciones.
- Pendiente de calibración igual a cero.
- Número insuficiente de estándares.
- NaN en datos cargados.
- Advertencia de extrapolación.
- Reproducibilidad con `numpy.random.default_rng(seed)`.

## Referencias de la práctica

Utilice las referencias bibliográficas de la guía docente/laboratorio de su curso. Este proyecto no sustituye la bibliografía institucional ni los protocolos reales del laboratorio.

## Licencia

MIT. Consulte `LICENSE`.

## Autor

**[Nombre del autor / institución]** — campo editable.
