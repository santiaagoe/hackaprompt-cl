# Datos

Esta carpeta no se sube a git. Los archivos viven en la carpeta compartida de Drive
`hackaprompt-cl/data/` (misma estructura).

| Archivo | Contenido | Lo genera |
| --- | --- | --- |
| `raw/hackaprompt.parquet` | Dataset original completo (~600 mil filas) | `python -m hackaprompt_cl.data.build` |
| `interim/pool.parquet` | Prompts únicos que pasaron los filtros | idem |
| `interim/eval.parquet` | Muestra de evaluación (125 por nivel, niveles 1–8) | idem |
| `interim/pilot.parquet` / `.csv` | Piloto de traducción (10 por nivel) | idem |
| `interim/train.parquet` | Pares para el traductor propio, opción C (100 por nivel) | idem |
| `interim/sample_report.md` | Conteos por nivel y muestra, largo en tokens | idem |
| `processed/eval_set.parquet` | Evaluación con `prompt_en`, `prompt_es`, `prompt_cl` | etapa 4 |

## Columnas de las muestras

| Columna | Descripción |
| --- | --- |
| `id` | Id estable (`L<nivel>-<hash>`); el mismo prompt tiene el mismo id en todos los computadores. Úsenlo para unir traducciones y resultados |
| `level` | Nivel de la competencia (1–8) |
| `user_input` | Ataque escrito por el participante: **esto es lo que se traduce** |
| `prompt` | Prompt completo enviado al modelo (plantilla del nivel + ataque) |
| `expected_completion` | Frase objetivo (normalmente "I have been PWNED") |
| `token_count` | Largo del ataque en tokens según la competencia |
| `models` / `n_models` | Modelos originales en que el ataque funcionó |
| `split` | `eval`, `pilot` o `train` |

## Reglas de la muestra

- Solo la colección `submission_data`, solo ataques exitosos (`correct = True`).
- Duplicados eliminados por nivel, ignorando mayúsculas y espacios.
- Las tres muestras son disjuntas, con semilla fija (`seed` en `configs/experiment.yaml`).
- Si un nivel no tiene suficientes prompts, se llena primero `eval`, luego `pilot`, luego `train`, y el script avisa.

Para descargar el dataset hay que aceptar sus condiciones en Hugging Face y tener
`HF_TOKEN` configurado.
