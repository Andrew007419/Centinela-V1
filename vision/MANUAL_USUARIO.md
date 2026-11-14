# CENTINELA·AGAVE — Manual de usuario del detector local

Versión de instrucciones: 2026-11-13. Dirigido a Windows/PowerShell y Python 3.11.
Este manual usa los scripts de CENTINELA_AGAVE_Integracion_Local.zip. No hace falta volver a entrenar para usar best.pt.

## 1. Qué hace y qué significa el resultado

Detecta agaves visibles en fotos y videos; una sola clase `agave`. Fotos: caja, confianza, ID consecutivo por foto y conteo. Video: seguimiento ByteTrack, conteo por cuadro e IDs temporales. Los IDs pueden cambiar tras oclusión o reaparición; no son identificadores permanentes de parcela. No sumar cuadros ni IDs como inventario único.

No mide masa, azúcares, madurez, salud o tamaño en metros. Modelo entrenado con vistas aéreas; no se ha validado desde la cámara terrestre del robot. La confianza no es porcentaje de madurez.

## 2. Archivos que necesita

- Carpeta del repositorio clonado con `vision/`, `software/`, `ipo/` y `docs/`.
- Los scripts del paquete, dentro de `vision/src/`.
- Pesos reales `vision/models/best.pt`, descargados de la corrida de Drive `CENTINELA_AGAVE/vision/runs/agave_v1-2/weights/best.pt`.
- Fotos JPG/PNG y video MP4 autorizado para demostración. El paquete no incluye pesos, fotos ni video.
- Internet para instalar dependencias la primera vez. El detector de imágenes no usa la API de Roboflow. Algunas dependencias del tracking pueden requerir instalación inicial; el paquete incluye lap.

El ZIP contiene una carpeta vision/. Copiar su contenido sobre vision/ del clon, sin crear vision/vision/. Comparar los archivos existentes antes de reemplazarlos; no incluye ni debe reemplazar software/, ipo/, docs/ o .git/.

## 3. Preparación inicial y respaldo de cambios

Abrir VS Code > Archivo > Abrir carpeta > seleccionar la raíz del clon > Terminal > Nueva terminal (PowerShell).

```powershell
Get-Location
Get-ChildItem
git rev-parse --show-toplevel
git status
git remote -v
```

Si `not a git repository`, entrar en el clon correcto: no ejecutar git init para reparar una ubicación equivocada. Si la carpeta es un ZIP sin Git, clonar el repositorio real y copiar vision allí. Si hay cambios de otros trabajos, guardarlos en su rama antes de cambiar; no usar reset --hard ni limpiar archivos.

Con el árbol limpio y la rama principal llamada main:

```powershell
git switch main
git pull --ff-only origin main
git switch -c vision/entrega-ia
```

Si main o la rama de trabajo tienen otro nombre, usar el nombre real. Si vision/entrega-ia ya existe: `git switch vision/entrega-ia`; no recrearla. `--ff-only` puede rechazar divergencias: detenerse y revisar, no forzar el push.

## 4. Copiar el código, pesos y evidencias

1. Extraer el ZIP de integración fuera del repositorio.
2. Copiar los archivos de su vision/ al vision/ del clon, comparando con cambios locales.
3. Descargar best.pt de Drive y guardarlo en vision/models/best.pt. No renombrar yolov8n.pt a best.pt: el primero es el modelo base, no tu entrenamiento.
4. Para entregar evidencia, abrir vision/EXPORTAR_DESDE_COLAB.txt, copiar su contenido a una celda de Colab y ejecutar. Monta Drive, empaqueta los pesos, configuración y evaluación si está en la ruta conocida; no reentrena ni reevalúa test.
5. Descargar entrega_ia_colab.zip y copiar su vision/ sobre la del clon, preservando los scripts. Revisar que contiene modelos/manifiesto y evidencias. Si la evaluación estaba en otra ruta, copiar esa carpeta real a vision/evidencias/.
6. Guardar también el notebook de Colab: Archivo > Descargar > Descargar .ipynb. Conservar la versión completa en Drive; antes de publicarla eliminar claves y salidas sensibles. Puede usar Colab Secrets; no publicar una API key incrustada.

Las métricas del exportador están identificadas como reportadas por el responsable; conservar el JSON original de evaluación. El freeze al empaquetar describe esa sesión; no prueba las versiones históricas si ya se reinició o actualizó.

## 5. Instalar en Windows

```powershell
py -0p
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r vision/requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m compileall vision/src
.\.venv\Scripts\python.exe -m vision.src.usar_modelo --help
```

Si no existe Python 3.11, instalarlo y volver a abrir la terminal. No es necesario activar el entorno; llamar su python explícitamente evita la política de ejecución de PowerShell. Usar requirements.txt directo para instalación local; no imponer el freeze CUDA/Linux de Colab a Windows.

Verificar el modelo:

```powershell
Get-Item vision/models/best.pt
Get-FileHash vision/models/best.pt -Algorithm SHA256
.\.venv\Scripts\python.exe -c "from ultralytics import YOLO; print(YOLO('vision/models/best.pt').names)"
```

Debe mostrar `{0: 'agave'}`. Comparar hash con manifiesto.json, ignorando mayúsculas/minúsculas.

## 6. Detectar una fotografía

Crear carpetas y copiar una fotografía autorizada como prueba.jpg. Cambiar su extensión en el comando si es PNG; no basta renombrar extensiones.

```powershell
New-Item -ItemType Directory -Force vision/samples,vision/outputs,vision/evidencias,vision/notebooks
.\.venv\Scripts\python.exe -m vision.src.usar_modelo imagen --entrada "vision/samples/prueba.jpg" --json "vision/outputs/prueba.json"
```

La terminal indica conteo, lista de detecciones, tiempo_ms y ruta de imagen anotada. Esta versión dibuja cajas verdes y números pequeños para evitar etiquetas superpuestas; la confianza está en JSON. Cada foto recibe un nombre de salida único.

Abrir el resultado:

```powershell
$r = Get-Content vision/outputs/prueba.json -Raw | ConvertFrom-Json
$r.conteo
Invoke-Item $r.imagen_anotada
```

`tiempo_ms` mide predict en CPU, sin cargar pesos, leer foto ni escribir salida. La primera inferencia puede incluir inicialización; medir después de calentamiento.

El umbral predeterminado es 0.25. Se puede explorar en fotos de demostración o validación con `--conf 0.40`, pero no elegir el umbral usando test y seguir llamándolo prueba independiente. Mayor umbral puede omitir más plantas.

## 7. Video y seguimiento

Colocar un video real autorizado de agaves en vision/samples/prueba.mp4. Puede ser público con licencia/atribución; no se exige viajar al campo. Si no hay video, registrar esta entrega como pendiente. Una sucesión de fotos de test no valida seguimiento de video real.

```powershell
.\.venv\Scripts\python.exe -m vision.src.usar_modelo video --entrada "vision/samples/prueba.mp4" --salida "vision/outputs/demo.mp4"
Invoke-Item vision/outputs/demo.mp4
```

Genera demo.mp4 y demo.json. El JSON incluye conteo_por_cuadro, ids, ids_observados, máximo simultáneo y fps_proceso. IDs temporales; IDs observados no son plantas únicas. El video se procesa secuencialmente y en CPU; puede tardar más que la duración del clip. No ejecutar con la misma ruta de entrada y salida. Cambiar el nombre de salida para conservar una demo anterior.

Para un navegador puede necesitar H.264. Si tiene FFmpeg instalado:

```powershell
ffmpeg -version
ffmpeg -i vision/outputs/demo.mp4 -c:v libx264 -pix_fmt yuv420p -an vision/outputs/demo_web.mp4
```

No sustituir el original hasta revisar la salida. Grabar también un clip de pantalla del programa funcionando. Entregar clip principal y respaldo en Drive con permisos para los revisores.

## 8. Medir velocidad local y error de conteo

```powershell
.\.venv\Scripts\python.exe -m vision.src.medir_latencia --carpeta vision/samples
```

Guardar vision/evidencias/latencia_local.json. Hace 5 calentamientos y al menos 30 mediciones; repite fotos si hay menos de 30 y registra cuántas son distintas. Para evidencia representativa, usar varias escenas. Documentar además RAM, CPU exacta, sistema, resoluciones y condiciones. No confundir 3.1 ms de inferencia reportados en Colab con rendimiento de laptop/Jetson.

Para MAE, crear vision/samples/conteos.csv con encabezado `ruta,real`. Cada fila contiene una ruta real y su conteo manual revisado, por ejemplo `vision/samples/prueba.jpg,NUMERO_REAL`; reemplazar NUMERO_REAL por un entero antes de ejecutar. Añadir otras escenas y negativos, no copiar un valor supuesto.

```powershell
.\.venv\Scripts\python.exe -m vision.src.evaluar_conteo --csv vision/samples/conteos.csv
```

Genera vision/evidencias/conteo.json con MAE, sesgo y máximo. Cero conteo real es válido para negativos. Este conjunto de revisión local no debe presentarse como nuevo test independiente si se usó para depurar o ajustar.

Prueba de error esperado:

```powershell
.\.venv\Scripts\python.exe -m vision.src.usar_modelo imagen --entrada vision/samples/no_existe.jpg
```

Debe terminar con error comprensible y código de salida distinto de cero; no devolver conteo cero ocultando el problema. Un compañero debe repetir instalación, foto y video en un entorno nuevo y registrar fecha, equipo y resultado.

## 9. Contrato para integrar al panel

El paquete no crea ni reemplaza el panel. La persona de software importa:

```python
from vision.src.inferencia import detectar, procesar_video
resultado = detectar(ruta_imagen)
# resultado: conteo, detecciones[{id,bbox,confianza}], imagen_anotada, tiempo_ms
resultado_video = procesar_video(ruta_video, ruta_salida)
# conteo_por_cuadro, video_anotado y campos adicionales
```

Las variables de rutas las define el panel al guardar el archivo subido. No pegar estas líneas sin adaptarlas en un app.py existente. Ejecutar desde raíz y añadir PYTHONPATH si el lanzador lo necesita. Probar importación y manejo de errores con software; no marcar integración completa sin probarla. Modelo de fotos cacheado por proceso: para concurrencia real usar bloqueo/servicio; demo secuencial.

## 10. Documentación de la entrega

Archivos DATASET.md, METRICAS.md y RESUMEN.md ya contienen hechos comunicados en la conversación, con pendientes explícitos. Completar ENLACES_IA.md con enlaces reales; agregar referencia a este archivo en docs/ENLACES.md sin borrar enlaces de otros roles.

Resultados reportados, no medidos de nuevo por quien preparó este paquete:

| Métrica test | Valor |
|---|---:|
| Precisión | 0.9674 |
| Recall | 0.9700 |
| mAP50 | 0.9889 |
| mAP50-95 | 0.5715 |

147 imágenes test. No es exactitud universal ni rendimiento probado desde robot. P/R resumidos del evaluador no equivalen automáticamente a P/R a conf=0.25.

Revisar contra la lista del manual original:

| Entrega | Estado y acción |
|---|---|
| Dataset y división | 4143/356/147; respaldo en Drive; documentar atribución, negativos, cajas por split y aumentaciones reales. |
| Entrenamiento reproducible | Guardar notebook completo con descarga, unificación, limpieza y entrenamiento; args.yaml y results.csv. entrenar.py no reemplaza esas etapas previas. |
| Pesos | Copiar best.pt; hash, tamaño, manifiesto y acceso de descarga. |
| Dependencias | Freeze de Colab disponible al empaquetar y lock local tras pruebas; registrar procedencia. |
| Test | Guardar JSON, curvas, matriz y ejemplos de errores originales. |
| Inferencia | Ejecutar foto y video, comprobar JSON y salidas. |
| Conteo | Medir MAE/sesgo/máximo con referencias manuales; pendiente hasta ejecutar. |
| Borde | Medir CPU local y documentar hardware; Jetson es plan, no ejecución probada. |
| Demo | Video real anotado, clip de pantalla y respaldo con fuente/licencia. |
| Panel | Probar imports, formato y manejo de errores junto al responsable. |
| Resumen | Actualizar RESUMEN.md, máximo 10 líneas. |
| Reproducción | Compañero instala y prueba desde cero; registrar resultado. |

## 11. Subir avances a GitHub

Agregar líneas de vision/GITIGNORE_IA.txt al .gitignore existente (no reemplazarlo). No subir API keys, .venv, muestras pesadas, videos, runs o pesos con este flujo; pesos se entregan por Drive con enlace y hash para cualquier tamaño. Aunque el manual anterior permitía pesos pequeños en Git, usar Drive aquí mantiene el repositorio ligero.

No ejecutar comandos para borrar archivos rastreados a ciegas. .gitignore no deja de rastrear algo ya commiteado: si `git ls-files vision/models` muestra pesos ya rastreados, revisar primero antes de cambiarlos.

```powershell
.\.venv\Scripts\python.exe -m pip freeze | Out-File -Encoding utf8 vision/requirements-local-lock.txt
git status --short
git check-ignore vision/models/best.pt
```

Añadir solo archivos del trabajo; incluir evidencias ligeras propias sin datos sensibles:

```powershell
git add .gitignore vision/src vision/__init__.py vision/requirements.txt vision/requirements-local-lock.txt
git add vision/DATASET.md vision/METRICAS.md vision/RESUMEN.md vision/ENLACES_IA.md
git add vision/MANUAL_USUARIO.md vision/models/README.md vision/GITIGNORE_IA.txt vision/EXPORTAR_DESDE_COLAB.txt
```

Si añadió evidencia ligera a vision/evidencias/, ejecutar `git add vision/evidencias`. Si editó docs/ENLACES.md, ejecutar `git add docs/ENLACES.md`. Revisar primero su contenido, tamaño y ausencia de claves; no agregar el notebook por defecto.

```powershell
git diff --cached --stat
git diff --cached
git commit -m "feat(vision): integrar detector de agaves y documentar resultados"
git push -u origin vision/entrega-ia
```

Abrir el repositorio en GitHub > Compare & pull request > base main > compare vision/entrega-ia. Describir comportamiento, métricas y pruebas realmente ejecutadas; dejar pendientes explícitos. No afirmar pruebas locales exitosas hasta realizarlas. El push sube la rama; el PR solicita integrar a main.

Después de que el equipo apruebe y fusione el PR, con árbol limpio:

```powershell
git switch main
git pull --ff-only origin main
```

Compañeros en main con árbol limpio ejecutan el mismo pull. Si tienen cambios locales o trabajan en otra rama, deben guardarlos e integrar main según su flujo; no forzar ni ejecutar reset --hard. Para siguientes avances en la rama de IA, commit y git push.

## 12. Errores frecuentes

| Mensaje/síntoma | Acción |
|---|---|
| Faltan pesos | Copiar best.pt real a vision/models/. |
| Clase distinta | Revisar que descargó agave_v1-2/weights/best.pt. |
| ModuleNotFoundError vision | Ejecutar desde raíz y usar -m vision.src.usar_modelo. |
| No encuentra Python 3.11 | Instalar Python o seleccionar una versión compatible conscientemente. |
| Imagen ilegible | Revisar ruta/extensión/archivo; no interpretar como cero agaves. |
| Video ilegible o sin FPS | Probar en reproductor; recodificar y revisar entrada. |
| Video no abre en web | Convertir a H.264/yuv420p. |
| Missing lap | Instalar vision/requirements.txt con el Python del entorno. |
| Cero o malas detecciones | Revisar perspectiva, tamaño de plantas y dominio; no es garantía fuera de vistas aéreas. |
| not a git repository | Abrir el clon, no una subcarpeta ajena o ZIP extraído. |
| Push rechazado | Revisar rama/remoto y cambios; no usar force para resolver sin análisis. |

## 13. Estado de validación y referencias

Código derivado del manual adjunto, con lanzador CLI, dibujo de IDs de foto y utilidades locales añadidas. Se comprobó sintaxis y contratos con dobles de prueba; no se ejecutó inferencia con sus pesos reales en este entorno. Los resultados reales de Colab son los comunicados por el usuario. Instalación y ejecución local quedan por comprobar.

Ultralytics tracking: https://docs.ultralytics.com/modes/track/
Git push: https://git-scm.com/docs/git-push
Git pull: https://git-scm.com/docs/git-pull
