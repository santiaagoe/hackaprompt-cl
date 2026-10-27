# Notebooks

Convención de nombres: `NN_tema_autor.ipynb` (ej. `02_piloto_traduccion_santiago.ipynb`).

## Primera celda de todo notebook en Colab

```python
from google.colab import drive, userdata
drive.mount("/content/drive")

!git clone https://github.com/<organizacion>/hackaprompt-cl.git
%cd hackaprompt-cl
!pip install -q -e ".[translate,quality,evaluate]"

import os
os.environ["HF_TOKEN"] = userdata.get("HF_TOKEN")   # Secrets de Colab, nunca en el código

# Datos compartidos en Drive, enlazados donde el código los espera
!rm -rf data && ln -s /content/drive/MyDrive/hackaprompt-cl/data data
!rm -rf results && ln -s /content/drive/MyDrive/hackaprompt-cl/results results
```

Para trabajar en una rama: `!git switch feat/12-mi-rama` después del clone.
Para subir cambios desde Colab es más simple editar `src/` en el computador y
dejar el notebook solo para ejecutar.
