# Notebooks

Convención de nombres: `NN_tema_autor.ipynb` (ej. `02_piloto_traduccion_santiago.ipynb`).

## Primera celda de todo notebook en Colab

```python
from google.colab import drive, userdata
drive.mount("/content/drive")

!git clone https://github.com/santiaagoe/hackaprompt-cl.git
%cd hackaprompt-cl
!pip install -q -e ".[translate,quality,evaluate]"

import os
os.environ["HF_TOKEN"] = userdata.get("HF_TOKEN")   # Secrets de Colab, nunca en el código

import sys
sys.path.insert(0, "/content/hackaprompt-cl/src")   # pip install -e no se ve hasta reiniciar

# Datos compartidos en Drive: el código los lee y escribe ahí
os.environ["HACKAPROMPT_DATA_DIR"] = "/content/drive/MyDrive/hackaprompt-cl/data"
```

Para trabajar en una rama: `!git switch feat/12-mi-rama` después del clone.
Para subir cambios desde Colab es más simple editar `src/` en el computador y
dejar el notebook solo para ejecutar.
