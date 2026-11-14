# 03 · Contratos entre roles

Para que las piezas encajen sin esperar a que otra persona termine, cada rol entrega sus resultados **en el formato de este documento**. Si necesitas cambiar un formato, avisa por el chat y actualiza este archivo mediante Pull Request.

```
Visión (Int. 1) ──┐
                  ├──> Panel (Int. 3) ──> Video y pitch (Int. 4)
IPO (Int. 2) ─────┤
Datos (Int. 3) ───┘
Mecatrónica (Asesor) ──────────────────> Video y pitch (Int. 4)
```

## 1. Visión → Panel

**Archivo:** `vision/src/inferencia.py`
**Pesos:** `vision/models/best.pt` (si pesa más de 50 MB, va a Drive y se documenta el enlace).

```python
def detectar(ruta_imagen: str, conf: float = 0.25) -> dict:
    """Devuelve las plantas detectadas en una imagen."""
```

**Salida:**
```json
{
  "conteo": 12,
  "detecciones": [
    {"id": 1, "bbox": [x1, y1, x2, y2], "confianza": 0.87}
  ],
  "imagen_anotada": "ruta/a/imagen_con_cajas.jpg",
  "tiempo_ms": 85
}
```
También se entrega `procesar_video(ruta_video, salida) -> dict` con el conteo por cuadro y la ruta del video anotado.

## 2. IPO → Panel

**Archivo:** `ipo/src/api.py` (FastAPI). Se levanta con `uvicorn ipo.src.api:app --reload`.
**Función equivalente en Python:** `ipo/src/modelo.py: calcular_ipo(escenario, ...)`.

**Petición:**
```
GET /ipo?escenario=base&anio_inicio=2026&anio_fin=2034
```
`escenario` puede ser `optimista`, `base` o `pesimista`.

**Respuesta (los valores son un ejemplo de formato, no resultados):**
```json
{
  "escenario": "base",
  "factor_plantas_a_toneladas": {"min": 0.0, "base": 0.0, "max": 0.0, "unidad": "t/planta"},
  "ventana_maduracion_anios": [6, 7, 8],
  "serie": [
    {
      "anio": 2026,
      "oferta_madura_plantas": 0,
      "oferta_madura_t": 0,
      "demanda_t": 0,
      "ipo": 0.0,
      "ipo_min": 0.0,
      "ipo_max": 0.0
    }
  ],
  "supuestos": ["texto corto de cada supuesto usado"],
  "fuentes": ["texto corto de cada fuente"]
}
```
- `ipo_min` e `ipo_max` salen de la banda del factor plantas→toneladas.
- La respuesta siempre incluye `supuestos` y `fuentes`, para que el panel los muestre.

## 3. Datos → Panel e IPO

**Carpeta:** `data/processed/` (CSV pequeños, en UTF-8). Los archivos originales pesados quedan en Drive.

| Archivo | Columnas mínimas | Lo genera |
|---|---|---|
| `denue_312144_jalisco.csv` | `nombre`, `municipio`, `clave_mun`, `lat`, `lon`, `estrato_personal` | Integrante 3 |
| `comercio_2208_90.csv` | `periodo`, `valor_usd`, `volumen`, `unidad`, `destino` | Integrante 3 |
| `censo_3121_municipal.csv` | `municipio`, `clave_mun`, `anio`, `produccion_bruta`, `valor_agregado`, `personal_ocupado` | Integrante 3 |
| `inventario_agave.csv` | `anio`, `plantas`, `hectareas`, `fuente`, `definicion` | Integrante 2 (con apoyo de Int. 3) |

Las columnas pueden ajustarse a lo que traiga cada fuente. Lo importante es **documentar el cambio aquí** y mantener los nombres en minúsculas y sin acentos.

## 4. Mecatrónica → Entregables

| Entregable | Ruta | Formato |
|---|---|---|
| Renders ligeros | `mecatronica/renders/` | PNG, menos de 5 MB cada uno |
| BOM | `mecatronica/BOM.csv` | CSV con columnas `componente`, `fase`, `costo_usd_min`, `costo_usd_max`, `justificacion` |
| Animación y CAD | Drive (ver `docs/ENLACES.md`) | MP4 1080p a 30 fps, STEP y GLB |
| Limitaciones y fases | `mecatronica/LIMITACIONES_Y_FASES.md` | Markdown |

## 5. Todos → Entregables (Integrante 4)

Cada rol deja en su carpeta un `RESUMEN.md` de **máximo 10 líneas** con: qué hizo, resultado principal, limitación principal y qué decir si le preguntan. Es la materia prima del reporte y del pitch.

## 6. Convenciones comunes

- Idioma de la documentación: español. Nombres de código y variables: español o inglés, pero consistentes dentro de cada módulo.
- Archivos y carpetas en minúsculas, sin espacios ni acentos.
- Fechas en formato `AAAA-MM-DD`.
- Semillas aleatorias fijas (`seed=42`) para que los resultados se puedan reproducir.
- Cada cifra que aparezca en el panel, el reporte o el pitch debe poder rastrearse a una fuente o a un supuesto escrito.
