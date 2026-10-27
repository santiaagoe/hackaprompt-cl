# Registro de decisiones

| Fecha | Decisión | Por qué |
| --- | --- | --- |
| 2026-10-27 | Flujo GitHub Flow con PR y 1 aprobación | 5 personas, entregas continuas, ramas cortas |
| 2026-10-27 | Muestra de 1.000 prompts (125 x niveles 1–8) de Submissions | Ver definición del proyecto |
| 2026-10-27 | Modelo víctima: Llama 8B Instruct, temperatura 0 | Recomendación del auxiliar; corre en Colab |
| 2026-10-27 | Tres muestras disjuntas: eval 1.000, piloto 80, entrenamiento del traductor 800 | Que lo usado para ajustar o entrenar la traducción no contamine la evaluación |
| 2026-10-27 | Deduplicar por nivel ignorando mayúsculas y espacios; quedarse con la versión de menos tokens | Mismo ataque enviado a varios modelos; la competencia premiaba menos tokens |
| 2026-10-27 | Prueba base: piloto (80) en inglés sobre Llama 3.1 8B Instruct en 4 bits, greedy, 64 tokens | Conocer la tasa de éxito base antes de traducir: 983 de 1.000 ataques funcionaron en un solo modelo original |
| 2026-10-27 | Cada prompt va como un único mensaje de usuario, sin mensaje de sistema extra | Igual para inglés y español; el prompt ya incluye la plantilla del nivel |
