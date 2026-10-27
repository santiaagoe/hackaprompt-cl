# HackAPrompt en español chileno

Análisis de qué pasa con los ataques de inyección de prompts del dataset
[HackAPrompt](https://paper.hackaprompt.com) (EMNLP 2023) cuando se traducen a
español chileno nativo.

**Pregunta:** ¿cambia la tasa de éxito de los ataques (ASR) al pasar de inglés
a español neutro y a español chileno, evaluados sobre el mismo modelo (Llama)?

## Estructura

```
hackaprompt-cl/
├── configs/              # Parámetros del experimento (semilla, tamaños, modelos)
├── data/                 # NO se sube a git (ver data/README.md)
│   ├── raw/              # Dataset original descargado de Hugging Face
│   ├── interim/          # Muestra, traducciones intermedias (ES neutro)
│   └── processed/        # Dataset final EN / ES / ES-CL listo para evaluar
├── docs/                 # Definición del proyecto, decisiones, informe
├── notebooks/            # Notebooks de Colab: delgados, solo llaman a src/
├── results/              # Respuestas de Llama y métricas (NO se sube a git)
├── src/hackaprompt_cl/
│   ├── data/             # Descarga, filtrado y muestreo estratificado
│   ├── translate/        # Traductores: A (API), B (MarianMT/NLLB), C (LoRA propio)
│   ├── quality/          # Chequeos automáticos, chrF/COMET, chilenidad (Tulio)
│   └── evaluate/         # Ejecución sobre Llama y criterio de éxito
└── tests/                # Pruebas automáticas (corren en cada PR)
```

## Cómo empezar

```bash
git clone https://github.com/<organizacion>/hackaprompt-cl.git
cd hackaprompt-cl
python -m venv .venv && source .venv/bin/activate   # en Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install          # limpia outputs de notebooks y formatea antes de cada commit
pytest                      # debería pasar todo
```

En Google Colab, ver [notebooks/README.md](notebooks/README.md).

## Flujo de trabajo

Usamos **GitHub Flow**: `main` siempre funciona, todo cambio entra por una rama
corta y un Pull Request revisado por otra persona. Las reglas completas están en
[CONTRIBUTING.md](CONTRIBUTING.md). Léanlo antes del primer commit.

## Etapas del proyecto

| Etapa | Carpeta | Issue |
| --- | --- | --- |
| 1. Descargar y muestrear 1.000 prompts | `src/hackaprompt_cl/data` | |
| 2. Piloto de traducción (80 prompts) | `src/hackaprompt_cl/translate` | |
| 3. Entrenar traductor propio (C) | `src/hackaprompt_cl/translate` | |
| 4. Traducir y medir calidad | `src/hackaprompt_cl/quality` | |
| 5. Correr EN / ES / ES-CL sobre Llama | `src/hackaprompt_cl/evaluate` | |
| 6. Análisis estadístico e informe | `notebooks/`, `docs/` | |

## Equipo

| Integrante | Área principal |
| --- | --- |
| | Datos y muestreo |
| | Traducción (A y B) |
| | Traductor propio (C) |
| | Calidad y evaluación humana |
| | Evaluación en Llama y análisis |
