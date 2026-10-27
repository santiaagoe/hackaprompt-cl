# Cómo trabajamos (GitHub Flow)

## Las 5 reglas

1. **`main` siempre funciona.** Nadie hace push directo a `main`; está protegida.
2. **Una tarea = un issue = una rama.** Antes de programar, crea o asígnate un issue.
3. **Ramas cortas.** Idealmente se fusionan en 1–3 días. Si crece mucho, divídela.
4. **Todo entra por Pull Request** con al menos **1 aprobación** de otra persona y
   las pruebas automáticas en verde.
5. **Datos y resultados no van a git.** Van a la carpeta compartida de Drive
   (o al dataset privado de Hugging Face). En git solo va el código que los genera.

## Paso a paso

```bash
# 1. Partir siempre desde main actualizado
git switch main
git pull

# 2. Crear la rama (tipo/numero-issue-descripcion-corta)
git switch -c feat/12-muestreo-estratificado

# 3. Trabajar y hacer commits pequeños
git add src/hackaprompt_cl/data/sample.py
git commit -m "feat(data): muestreo estratificado por nivel"

# 4. Subir la rama y abrir el Pull Request en GitHub
git push -u origin feat/12-muestreo-estratificado
```

En el PR escribe `Closes #12` para que el issue se cierre solo al fusionar.

Si `main` avanzó mientras trabajabas:

```bash
git switch main && git pull
git switch feat/12-muestreo-estratificado
git merge main          # resolver conflictos si aparecen, luego commit y push
```

## Nombres de ramas

| Prefijo | Para qué | Ejemplo |
| --- | --- | --- |
| `feat/` | Funcionalidad nueva | `feat/8-traductor-marian` |
| `fix/` | Corrección de un error | `fix/15-normalizacion-pwned` |
| `exp/` | Experimento o notebook exploratorio | `exp/21-piloto-80-prompts` |
| `docs/` | Documentación e informe | `docs/30-seccion-hipotesis` |

## Mensajes de commit

Formato: `tipo(área): qué cambió`, en presente y en español.

- `feat(translate): agregar pipeline MarianMT a español neutro`
- `fix(evaluate): ignorar punto final al comparar con la frase objetivo`
- `docs: explicar criterio de éxito relajado`

## Revisión de Pull Requests

- Revisa dentro de **24 horas** hábiles; si no puedes, avisa en el grupo.
- Fusiona quien abrió el PR, una vez aprobado, con **Squash and merge**
  (deja un solo commit limpio en `main`).
- Borra la rama después de fusionar (GitHub ofrece el botón).

## Notebooks

- La lógica va en `src/`; el notebook solo importa funciones y muestra resultados.
  Así los diffs son legibles y no hay conflictos imposibles de resolver.
- `pre-commit` borra los outputs de los notebooks antes de cada commit
  (`nbstripout`). No lo desactives.
- Un notebook por persona por experimento: `notebooks/03_piloto_traduccion_santiago.ipynb`.

## Reproducibilidad

- Todo parámetro (semilla, tamaños, nombre exacto del modelo, temperatura) vive en
  `configs/experiment.yaml`, no escrito a mano en el código.
- Cada archivo de resultados guarda la versión del commit con que se generó.
- Claves de API en variables de entorno o en los *Secrets* de Colab, **nunca** en el código.
