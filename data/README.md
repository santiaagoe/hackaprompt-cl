# Datos

Esta carpeta no se sube a git. Los archivos viven en la carpeta compartida de Drive
`hackaprompt-cl/data/` (misma estructura).

| Carpeta | Contenido | Lo genera |
| --- | --- | --- |
| `raw/` | Dataset original de Hugging Face | `src/hackaprompt_cl/data/download.py` |
| `interim/` | `sample.parquet`, `pilot.parquet`, `es_neutro.parquet` | muestreo y traducción paso 1 |
| `processed/` | `eval_set.parquet` con columnas `prompt_en`, `prompt_es`, `prompt_cl` | traducción final |

Para descargar el dataset hay que aceptar sus condiciones en Hugging Face y tener
`HF_TOKEN` configurado.
