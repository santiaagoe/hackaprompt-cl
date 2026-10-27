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
git clone https://github.com/santiaagoe/hackaprompt-cl.git
cd hackaprompt-cl
python -m venv .venv && source .venv/bin/activate   # en Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install          # limpia outputs de notebooks y formatea antes de cada commit
pytest                      # debería pasar todo
```

En Google Colab, ver [notebooks/README.md](notebooks/README.md).

## Dónde trabajar

El código se escribe en el computador y solo lo que necesita GPU se ejecuta en
Colab o Kaggle. Los notebooks no tienen lógica propia: clonan el repo y llaman
funciones de `src/`.

| Dónde | Para qué |
| --- | --- |
| **Computador** (VS Code + Git) | Escribir `src/`, pruebas y configs; ramas, commits y PRs. Todo lo que no necesita GPU: descarga y muestreo, chequeos de calidad, criterio de éxito, análisis estadístico |
| **Google Colab** | Lo que necesita GPU: traducción (MarianMT/NLLB), Llama, COMET, Tulio, pruebas del LoRA |
| **Kaggle Notebooks** | Corridas largas: experimento completo y entrenamiento del traductor propio (C) |
| **Drive compartido** (`hackaprompt-cl/`) | Datos (`data/`) y resultados (`results/`). Nunca en Git |

### Ciclo de trabajo

1. **Computador:** crear la rama, escribir la función en `src/` con su prueba,
   correr `pytest` y subir la rama (`git push`).
2. **Colab / Kaggle:** clonar esa rama (`git clone -b <rama> ...`), ejecutar con
   GPU y guardar los resultados en Drive.
3. **Si hay que corregir algo:** se corrige en el computador, se sube, y en el
   notebook basta con `!git pull` y volver a ejecutar.
4. **Cuando funciona:** abrir el Pull Request.

Si Colab corta la sesión no se pierde código, porque vive en GitHub; los
scripts largos guardan resultados parciales en Drive para poder retomar.

### A tener en cuenta

- **Llama necesita acceso:** cada integrante que lo ejecute debe aceptar la
  licencia del modelo en Hugging Face y guardar su `HF_TOKEN` en los *Secrets*
  de Colab (o en `.env` en local).
- **Backend del modelo víctima:** en local se puede usar Ollama (Mac con chip M
  o PC con GPU de 8 GB o más). En Colab y Kaggle se usa `transformers` en 4 bits
  o `vLLM`. Se elige con `victim.backend` en `configs/experiment.yaml`.

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
