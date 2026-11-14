# CENTINELA·AGAVE

> El radar de oferta madura del campo agavero. Convierte mediciones del campo en un pronóstico verificable de cuánta agave madurará y cuánta puede absorber la industria, para que el pequeño productor negocie con datos.

**Hackathon Jalisco Internacional 2026 · Reto 03 · Industria 4.0**
Problemática: desplome y volatilidad del precio del agave para pequeños productores jaliscienses (Altos Sur y Valles).

---

## Qué se construye en 4 días (MVP)

| Pieza | Estado objetivo |
|---|---|
| Modelo de visión (YOLOv8) que detecta y cuenta plantas de agave | Funcionando, con métricas en datos no vistos |
| Modelo de oferta madura por cohortes + Índice de Presión de Oferta (IPO) | Funcionando, con 3 escenarios y un endpoint |
| Panel web con 3 secciones y datos oficiales (DENUE, comercio exterior, Censo) | Navegable y reproducible |
| Diseño del robot (CAD, BOM, animación mínima de 10 s) | Vistas, lista de componentes y clip |
| Reporte, infografía, manual, pitch, video y ensayo | Entregados y ensayados |

El robot **no se construye** en esta fase. Se diseña, se anima y se plantea su prototipo por fases.

## Equipo y responsabilidades

| Rol | Carpeta | Prefijo de rama | Toca código |
|---|---|---|---|
| Asesor mecatrónica (dueño del robot) | `mecatronica/` | `mecatronica/` | No |
| Integrante 1 · Visión | `vision/` | `vision/` | Sí |
| Integrante 2 · IPO y demanda | `ipo/` | `ipo/` | Sí |
| Integrante 3 · Software y datos | `software/` y `data/` | `software/` | Sí |
| Integrante 4 · Entregables y defensa | `entregables/` | `entregables/` | No |

El detalle de cada rol está en el `README.md` de su carpeta.

## Estructura del repositorio

```
centinela-agave/
├── README.md                  <- este archivo
├── docs/
│   ├── 01_PROYECTO.md          <- problema, alcance y datos
│   ├── 02_GIT_Y_GITHUB.md      <- cómo trabajar con ramas, paso a paso
│   ├── 03_CONTRATOS_ENTRE_ROLES.md  <- formatos para que las piezas encajen
│   ├── 04_PLAN_4_DIAS.md       <- qué hace cada quien cada día
│   └── ENLACES.md              <- enlaces a Drive y recursos
├── mecatronica/               <- CAD, BOM, renders, animación
├── vision/                    <- dataset, entrenamiento YOLOv8, inferencia
├── ipo/                       <- cohortes, demanda, escenarios, API
├── software/                  <- panel web y ETL de datos
├── data/                      <- datos procesados (los pesados van a Drive)
├── entregables/               <- reporte, infografía, manual, pitch, video
└── .github/                   <- plantilla de Pull Request y CODEOWNERS
```

## Inicio rápido

Para correr el panel y la API del IPO en tu computadora (probado con Python 3.13 en Windows). Todos los comandos se ejecutan desde la raíz del repositorio:

```bash
python -m venv .venv
source .venv/bin/activate            # Windows (PowerShell): .venv\Scripts\Activate.ps1
pip install -r software/requirements.txt
pip install -r ipo/requirements.txt
pip install -r vision/requirements.txt

python -m pytest -q ipo/tests        # tests del IPO (33)

# Terminal 1: API del IPO (http://127.0.0.1:8000/docs)
uvicorn ipo.src.api:app --reload

# Terminal 2: panel (http://localhost:8501)
streamlit run software/src/app.py
```

- Instala los tres `requirements.txt` en ese orden. La instalación tarda unos 3 minutos, sobre todo por PyTorch (lo trae `ultralytics`, de `vision/requirements.txt`).
- Los tests se corren con `python -m pytest`. Un `pytest` a secas **falla** (`No module named 'ipo'`), porque no encuentra el paquete `ipo` desde la raíz.
- En Windows, clona el repositorio en una ruta corta (menos de unos 60 caracteres, por ejemplo `C:\proyectos\Centinela-V1`). Con rutas muy largas la instalación de `streamlit` falla con `WinError 206` (nombre de archivo demasiado largo).
- Si la API no está corriendo, el panel funciona con datos de ejemplo marcados como tales.
- Más detalle del panel y de los datos en `software/README.md`.

## Cómo empezar

1. Lee `docs/01_PROYECTO.md` (10 minutos).
2. Sigue `docs/02_GIT_Y_GITHUB.md` para clonar el repo y crear tu rama.
3. Lee el `README.md` de tu carpeta y trabaja sobre tu lista de tareas.
4. Revisa `docs/03_CONTRATOS_ENTRE_ROLES.md` antes de entregar algo que otra persona va a usar.

## Reglas del equipo

1. **Nadie sube directo a `main`.** Todo entra por Pull Request.
2. **Una rama por tarea**, con el prefijo de tu rol.
3. **Archivos pesados a Drive** (datasets, `.blend`, CAD, videos). En Git solo código, texto, tablas pequeñas e imágenes ligeras.
4. **Lo que no está medido se declara como supuesto.** No inventamos cifras.
5. **Si algo bloquea a otra persona, se avisa el mismo día.**
