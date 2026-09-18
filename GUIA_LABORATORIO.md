# GUÍA DE LABORATORIO

## Laboratorio Virtual de Espectrofotometría UV-Visible y Ley de Beer-Lambert

### 1. Datos generales

- **Asignatura:** Bioquímica
- **Práctica:** Espectrofotometría
- **Área temática:** Espectrofotometría UV-Visible, Ley de Beer-Lambert y cuantificación por calibración
- **Nivel:** primeros semestres de Medicina / Enfermería
- **Modalidad:** laboratorio virtual complementario a la práctica experimental
- **Duración sugerida:** 2–3 horas
- **Analito de la práctica:** azul de metileno
- **Solución madre:** 10 mg/L
- **Peso molecular usado en los cálculos:** 319.8 g/mol

## 2. Introducción

La espectrofotometría UV-Visible permite estudiar cómo una muestra atenúa radiación electromagnética a diferentes longitudes de onda. A partir de la intensidad de luz incidente y transmitida pueden calcularse la transmitancia y la absorbancia. Bajo condiciones apropiadas, la Ley de Beer-Lambert relaciona linealmente la absorbancia con la concentración.

En esta práctica virtual se reproducen tres etapas centrales: obtención de un espectro de absorción, construcción de una curva de calibración y estimación de una muestra desconocida. Los datos generados por la aplicación son **simulados con fines educativos**, salvo cuando el estudiante cargue datos propios.

## 3. Objetivo general

Analizar cuantitativamente la relación entre luz, absorbancia y concentración mediante simulaciones de espectrofotometría UV-Visible, preparación de diluciones, calibración lineal y determinación de una muestra desconocida.

## 4. Objetivos específicos

1. Calcular transmitancia, porcentaje de transmitancia y absorbancia a partir de intensidades de luz.
2. Determinar un λmax a partir de un espectro simulado o de datos cargados.
3. Preparar conceptualmente estándares de 0, 2, 4, 6, 8 y 10 mg/L a partir de una solución madre de 10 mg/L.
4. Relacionar ε, b y c mediante la Ley de Beer-Lambert.
5. Construir y analizar una curva de calibración A = mC + b0.
6. Estimar la concentración de una muestra desconocida e interpretar interpolación, extrapolación y error.

## 5. Fundamento teórico

### 5.1 Transmitancia

La transmitancia es la fracción de radiación que atraviesa una muestra:

\[
T=\frac{I}{I_0}
\]

### 5.2 Porcentaje de transmitancia

\[
\%T=100\frac{I}{I_0}
\]

### 5.3 Absorbancia

\[
A=-\log_{10}(T)=\log_{10}\left(\frac{I_0}{I}\right)
\]

### 5.4 Ley de Beer-Lambert

\[
A=\varepsilon b c
\]

donde ε es la absortividad molar, b el camino óptico y c la concentración molar.

### 5.5 Dilución

\[
C_1V_1=C_2V_2
\]

\[
C_2=\frac{C_1V_1}{V_2}
\]

### 5.6 Curva de calibración

\[
A=mC+b_0
\]

### 5.7 Muestra desconocida

\[
C=\frac{A-b_0}{m}
\]

No debe reemplazarse automáticamente por C = A/m si el intercepto no es exactamente cero.

## 6. Acceso al laboratorio virtual

- **URL de Streamlit:** ______________________________
- **Repositorio GitHub:** ____________________________

## 7. Guía de uso de la aplicación

1. Abra la aplicación.
2. Use el menú lateral para seleccionar el módulo.
3. Antes de modificar una variable, escriba una predicción en su hoja de trabajo.
4. Cambie sliders, selectores o entradas numéricas.
5. Observe las métricas y la gráfica.
6. Cuando corresponda, pulse **Registrar medición**.
7. Repita para varias condiciones.
8. Descargue los datos mediante CSV o Excel.
9. En **Laboratorio virtual completo**, verifique su progreso y genere el reporte final.

## 8. Variables experimentales

| Variable | Símbolo | Unidad | Tipo | Rango/condición | Función |
|---|---|---:|---|---|---|
| Intensidad incidente | I0 | u.a. | Independiente | > 0 | Fuente de radiación |
| Intensidad transmitida | I | u.a. | Independiente | 0 < I ≤ I0 | Radiación después de la muestra |
| Transmitancia | T | adimensional | Dependiente | 0 < T ≤ 1 | Fracción transmitida |
| Absorbancia | A | adimensional | Dependiente | ≥ 0 en el modelo básico | Atenuación logarítmica |
| Longitud de onda | λ | nm | Independiente | 440–800 nm | Define el punto del espectro |
| Concentración | c | mg/L, mol/L, µM | Independiente | ≥ 0 | Cantidad de analito |
| Absortividad molar | ε | L mol⁻¹ cm⁻¹ | Parámetro | > 0 | Sensibilidad intrínseca del modelo |
| Camino óptico | b | cm | Parámetro | > 0 | Longitud recorrida por la luz |
| Pendiente | m | A/(mg/L) | Resultado | depende de datos | Sensibilidad de calibración |
| Intercepto | b0 | A | Resultado | depende de datos | Señal predicha a C = 0 |
| Coeficiente de determinación | R² | adimensional | Resultado | 0–1 | Describe el ajuste lineal |

## 9. Experimento 1. Transmitancia y absorbancia

### Objetivo

Comprobar que la relación entre T y A es logarítmica.

### Predicción previa

¿Qué ocurrirá con A cuando I disminuya mientras I0 permanece constante?

### Procedimiento

1. Abra **Luz, transmitancia y absorbancia**.
2. Mantenga I0 = 100 u.a.
3. Evalúe I = 100, 50, 10 y 1 u.a. si el control lo permite.
4. Registre T, %T y A.
5. Pulse **Registrar medición** para las condiciones seleccionadas.
6. Compare con la tabla de referencia incluida en la aplicación.

### Tabla

| Ensayo | I0 | I | T | %T | A |
|---:|---:|---:|---:|---:|---:|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |

### Cálculo manual

Para una de las condiciones, calcule T y A manualmente y compare:

| Condición | Valor manual | Simulador | Diferencia | % error |
|---|---:|---:|---:|---:|
| T | | | | |
| A | | | | |

## 10. Experimento 2. Espectro de absorción y λmax

### Objetivo

Identificar el máximo de absorbancia en un espectro simulado.

### Procedimiento

1. Abra **Espectro de absorción**.
2. Mantenga inicialmente la configuración predeterminada.
3. Observe los puntos de 440 a 800 nm.
4. Registre λmax y Amax.
5. Modifique la posición nominal λ0 y el ancho σ.
6. Repita con ruido instrumental activado.
7. Descargue el CSV del espectro.

### Registro

| Condición | λ0 nominal (nm) | σ (nm) | Ruido | λmax detectado (nm) | Amax |
|---|---:|---:|---|---:|---:|
| Basal | | | | | |
| Cambio 1 | | | | | |
| Cambio 2 | | | | | |

### Preguntas

- ¿Por qué el λmax identificado puede cambiar ligeramente cuando se añade ruido?
- ¿Cómo influye el ancho de banda en la forma del espectro?
- ¿Por qué una medición cuantitativa suele realizarse cerca de λmax?

## 11. Experimento 3. Preparación de estándares

### Objetivo

Relacionar el volumen de solución madre con la concentración final.

### Procedimiento

1. Abra **Preparación de soluciones**.
2. Verifique la tabla de seis tubos.
3. Confirme manualmente las concentraciones 0, 2, 4, 6, 8 y 10 mg/L usando C1V1 = C2V2.
4. Convierta al menos dos concentraciones a mol/L usando PM = 319.8 g/mol.
5. Use la calculadora general de diluciones con un ejemplo adicional.

### Tabla de práctica

| Tubo | V stock (mL) | V agua (mL) | V final (mL) | C (mg/L) | C (mol/L) | C (µmol/L) |
|---|---:|---:|---:|---:|---:|---:|
| Blanco | 0 | 5 | 5 | | | |
| 1 | 1 | 4 | 5 | | | |
| 2 | 2 | 3 | 5 | | | |
| 3 | 3 | 2 | 5 | | | |
| 4 | 4 | 1 | 5 | | | |
| 5 | 5 | 0 | 5 | | | |

## 12. Experimento 4. Ley de Beer-Lambert

### Objetivo

Analizar independientemente el efecto de ε, b y c sobre A.

### Procedimiento

1. Abra **Ley de Beer-Lambert**.
2. Registre la condición inicial.
3. Pulse **Duplicar concentración** y observe A.
4. Regrese a una condición inicial y pulse **Duplicar camino óptico**.
5. Modifique ε.
6. Registre cada condición.

### Tabla

| Condición | ε (L mol⁻¹ cm⁻¹) | b (cm) | c (µM) | A | Predicción cumplida (sí/no) |
|---|---:|---:|---:|---:|---|
| Basal | | | | | |
| 2c | | | | | |
| 2b | | | | | |
| ε modificada | | | | | |

## 13. Experimento 5. Curva de calibración y muestra desconocida

### Objetivo

Ajustar una calibración y usarla para estimar una concentración desconocida.

### Procedimiento

1. Abra **Curva de calibración**.
2. Seleccione **Modo ideal**.
3. Registre m, b0, R² y n.
4. Examine la gráfica de residuos.
5. Cambie a **Modo experimental** y active ruido instrumental.
6. Compare m, b0 y R² con el modo ideal.
7. Abra **Muestra desconocida**.
8. Seleccione **Interpolación**.
9. Observe la absorbancia y estime la concentración antes de revelar.
10. Pulse **Revelar concentración real**.
11. Registre concentración estimada, real y error porcentual.
12. Repita con **Extrapolación** y analice por qué el resultado requiere mayor cautela.

### Tabla de calibración

| Estándar | C (mg/L) | A |
|---:|---:|---:|
| 1 | 0 | |
| 2 | 2 | |
| 3 | 4 | |
| 4 | 6 | |
| 5 | 8 | |
| 6 | 10 | |

### Resultados de regresión

| Parámetro | Valor |
|---|---:|
| m | |
| b0 | |
| R² | |
| Error estándar | |

### Muestra desconocida

| A muestra | C estimada (mg/L) | C real simulada (mg/L) | Error absoluto | Error relativo | Error (%) |
|---:|---:|---:|---:|---:|---:|
| | | | | | |

## 14. Experimento 6. Errores experimentales

### Objetivo

Reconocer cómo diferentes errores modifican la calibración.

### Procedimiento

1. Abra **Errores experimentales**.
2. Comience sin activar errores y registre m, b0 y R².
3. Active solo **Ruido instrumental**.
4. Active solo **Error de pipeteo**.
5. Active solo **Blanco incorrecto**.
6. Active solo **Luz parásita**.
7. Active solo **Concentración elevada / pérdida de linealidad**.
8. Si el tiempo lo permite, pruebe combinaciones.

### Tabla

| Condición | m | b0 | R² | Patrón observado | Interpretación |
|---|---:|---:|---:|---|---|
| Ideal | | | | | |
| Ruido | | | | | |
| Pipeteo | | | | | |
| Blanco incorrecto | | | | | |
| Luz parásita | | | | | |
| No linealidad | | | | | |

## 15. Investigación libre

Diseñe un experimento usando cualquier módulo de la aplicación.

- Pregunta de investigación:
- Hipótesis:
- Variable independiente:
- Variable dependiente:
- Variables controladas:
- Procedimiento:
- Número de mediciones:
- Resultado principal:
- Conclusión:

## 16. Carga de datos propios

La aplicación permite cargar CSV/XLSX en los módulos de espectro y calibración.

### Espectro

Columnas sugeridas:

```text
Wavelength,Absorbance
```

### Calibración

Columnas sugeridas:

```text
Concentration,Absorbance
```

Cuando se cargan datos propios, la aplicación los analiza directamente y no añade ruido simulado.

## 17. Preguntas de análisis

1. ¿Por qué la absorbancia no cambia linealmente con la transmitancia?
2. ¿Qué significado físico tiene que A = 0?
3. ¿Por qué λmax es útil para mejorar la sensibilidad de una medición?
4. ¿Cómo cambia la concentración final si V1 aumenta manteniendo V2 constante?
5. ¿Qué supuesto permite esperar una relación lineal entre A y c?
6. ¿Por qué un R² elevado no garantiza por sí solo que la calibración sea adecuada?
7. ¿Qué información adicional aportan los residuos?
8. ¿Qué efecto esperaría sobre b0 si el blanco está incorrectamente medido?
9. ¿Por qué la luz parásita puede producir desviación a absorbancias altas?
10. ¿Qué diferencia conceptual existe entre interpolación y extrapolación?
11. ¿Por qué la expresión c = (A-b0)/m es preferible a c = A/m cuando b0 no es cero?
12. ¿Qué diferencia existe entre concentración en mg/L y concentración molar?
13. ¿Cómo influye la longitud del camino óptico en A?
14. ¿Qué limitación del modelo simulado considera más importante al compararlo con un espectrofotómetro real?
15. ¿Qué control experimental adicional usaría para comprobar que un cambio de absorbancia se debe al analito y no a una interferencia?

## 18. Preguntas de pensamiento crítico

1. Si dos curvas de calibración presentan R² similares pero una muestra un patrón curvo de residuos, ¿qué conclusión metodológica extraería?
2. ¿Cómo diseñaría un experimento real para distinguir entre error de pipeteo y luz parásita?
3. ¿Qué variable no incluida explícitamente en este simulador podría alterar una medición real de absorbancia y cómo la controlaría?

## 19. Conclusiones

Redacte entre 3 y 5 conclusiones basadas exclusivamente en los resultados obtenidos. Cada conclusión debe relacionarse con al menos uno de los objetivos de la práctica.

## 20. Producto a entregar

1. Guía respondida.
2. Archivo `experimentos_espectrofotometria.xlsx` o CSV descargado de la aplicación.
3. Tabla de calibración.
4. Interpretación de residuos.
5. Cálculo manual de al menos una transmitancia/absorbancia y una dilución.
6. Resultado de la muestra desconocida.
7. Respuestas de análisis.
8. Conclusiones.

## 21. Criterios de evaluación

| Criterio | Peso |
|---|---:|
| Registro correcto de datos | 20 % |
| Cálculos y unidades | 20 % |
| Curva de calibración y residuos | 20 % |
| Interpretación y preguntas de análisis | 25 % |
| Conclusiones y pensamiento crítico | 15 % |

## 22. Nombre recomendado para los archivos

- `Grupo_Apellido_experimentos_espectrofotometria.xlsx`
- `Grupo_Apellido_reporte_espectrofotometria.html`

