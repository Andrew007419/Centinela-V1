"""Panel Centinela (Streamlit) · esqueleto del día 1.

Correr:  streamlit run software/src/app.py
"""
from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

import datos
from cliente_ipo import obtener_ipo

RAIZ = Path(__file__).resolve().parents[2]
RUTA_INFERENCIA = RAIZ / "vision" / "src" / "inferencia.py"
ESCENARIOS = ["optimista", "base", "pesimista"]
AVISO_IPO_REGIONAL = (
    "El **IPO es regional**: no hay datos de inventario por municipio. "
    "Los filtros de municipio solo afectan a DENUE y al Censo, **no al IPO**."
)

st.set_page_config(page_title="Centinela·Agave", page_icon="🌵", layout="wide")


# ---------- Utilidades ----------
@st.cache_data(ttl=60, show_spinner=False)
def ipo_cacheado(escenario: str):
    return obtener_ipo(escenario, 2026, 2034)


@st.cache_resource(show_spinner="Cargando módulo de visión…")
def cargar_modulo_vision():
    """Importa vision/src/inferencia.py una sola vez por proceso (conserva el modelo YOLO en memoria).

    Devuelve (modulo, motivo). Si la importación falla, modulo es None y motivo explica por qué;
    solo en ese caso el panel usa el resultado de ejemplo.
    """
    if not RUTA_INFERENCIA.exists():
        return None, "`vision/src/inferencia.py` no existe."
    try:
        spec = importlib.util.spec_from_file_location("inferencia", RUTA_INFERENCIA)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as e:  # dependencias faltantes (cv2, ultralytics), etc.
        return None, f"no se pudo importar ({type(e).__name__}: {e}). Instala `vision/requirements.txt`."
    if not hasattr(mod, "detectar"):
        return None, "`inferencia.py` no define `detectar()`."
    return mod, ""


@st.cache_data(show_spinner="Procesando con el modelo de visión (en CPU puede tardar)…", max_entries=3)
def inferir(contenido: bytes, sufijo: str, es_video: bool, conf: float) -> dict:
    """Corre detectar()/procesar_video() sobre el archivo subido y devuelve el resultado del contrato
    más los bytes del medio anotado (`imagen_bytes` o `video_bytes`). Se cachea por contenido, para
    que cambiar de pestaña o de escenario no reprocese el archivo."""
    vision, _ = cargar_modulo_vision()
    with tempfile.TemporaryDirectory() as d:
        entrada = Path(d) / f"entrada{sufijo}"
        entrada.write_bytes(contenido)
        if es_video:
            res = vision.procesar_video(str(entrada), str(Path(d) / "anotado.mp4"))
            res["video_bytes"] = Path(res["video_anotado"]).read_bytes()
        else:
            res = vision.detectar(str(entrada), conf=conf)
            res["imagen_bytes"] = Path(res["imagen_anotada"]).read_bytes()
    return res


def mostrar_resultado_imagen(res: dict) -> None:
    c1, c2 = st.columns([1, 2])
    c1.metric("Plantas detectadas", res["conteo"])
    c1.caption(f"Inferencia: {res.get('tiempo_ms', '—')} ms (solo `predict`, en CPU)")
    if res["detecciones"]:
        c1.dataframe(pd.DataFrame(res["detecciones"])[["id", "confianza"]], hide_index=True, width="stretch")
    c2.image(res["imagen_bytes"], caption="Detecciones (el número es el id de la foto)")


def mostrar_resultado_video(res: dict) -> None:
    c1, c2, c3 = st.columns(3)
    c1.metric("Máximo de agaves visibles a la vez", res["maximo_simultaneo"])
    c2.metric("IDs de seguimiento observados", res["ids_observados"])
    c3.metric("Velocidad de proceso", f"{res['fps_proceso']:.1f} cuadros/s")
    st.warning(res.get("advertencia", "Los IDs de seguimiento no equivalen a plantas únicas."))
    cuadros = pd.DataFrame(res["conteo_por_cuadro"])
    st.line_chart(cuadros.set_index("cuadro")["conteo"], y_label="Agaves visibles", x_label="Cuadro")
    st.video(res["video_bytes"])
    st.download_button("Descargar video anotado", res["video_bytes"], file_name="anotado.mp4", mime="video/mp4")
    st.caption("El video se codifica en mp4v; si el navegador no lo reproduce, descárgalo.")


def rangos_calendario(serie: pd.DataFrame, margen: float = 1.1) -> tuple[float, float]:
    """Topes de los ejes del calendario: máximo de los datos por `margen`. (oferta y demanda en millones de t, IPO)."""
    tope_oferta = max(float(serie["oferta_madura_t"].max()), float(serie["demanda_t"].max())) / 1e6 * margen
    tope_ipo = max(float(serie["ipo_max"].max()), float(serie["ipo"].max()), 1.0) * margen
    return tope_oferta, tope_ipo


VERDE = "#6DBE8C"  # verde agave (igual que .streamlit/config.toml)
LEYENDA_ARRIBA = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)


def columnas_tabla_censo() -> dict:
    """Encabezados legibles y anchos (en píxeles) que dejan ver completos los nombres; el municipio queda fijo al desplazar."""
    cc = st.column_config
    return {
        "municipio": cc.TextColumn("Municipio", width=150, pinned=True),
        "clave_mun": cc.TextColumn("Clave", width=80, help="Clave INEGI de 5 dígitos (Jalisco = 14)."),
        "confidencial": cc.TextColumn("Confidencial", width=120, help=datos.AVISO_CONFIDENCIAL),
        "unidades_economicas": cc.NumberColumn("Unidades económicas", width=190),
        "personal_ocupado": cc.NumberColumn("Personal ocupado", width=160),
        "produccion_bruta": cc.NumberColumn("Producción bruta (millones de pesos)", width=310),
        "valor_agregado": cc.NumberColumn("Valor agregado (millones de pesos)", width=300),
    }


def tarjetas_ipo(resp) -> None:
    """Tarjetas con el IPO del primer y último año de la serie del escenario elegido."""
    s = resp.datos["serie"]
    a, b = s[0], s[-1]
    ej = " (ejemplo)" if resp.es_ejemplo else ""
    ayuda = "IPO = oferta madura ÷ demanda. Arriba de 1.0 hay más agave maduro que demanda; la banda es {:.2f} a {:.2f}."
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"IPO {a['anio']}{ej}", f"{a['ipo']:.2f}", help=ayuda.format(a["ipo_min"], a["ipo_max"]))
    c2.metric(f"IPO {b['anio']}{ej}", f"{b['ipo']:.2f}", help=ayuda.format(b["ipo_min"], b["ipo_max"]))
    c3.metric(f"Oferta madura {b['anio']}{ej}", f"{b['oferta_madura_t'] / 1e6:.1f} M t", help="Millones de toneladas de agave maduro.")
    c4.metric(f"Demanda {b['anio']}{ej}", f"{b['demanda_t'] / 1e6:.1f} M t", help="Millones de toneladas que la industria puede absorber.")


def aviso_ejemplo_ipo(resp) -> None:
    if resp.es_ejemplo:
        st.warning("⚠️ **DATOS DE EJEMPLO**: la API del IPO no responde; "
                   "los números de las pestañas 2 y 3 no son reales.")
        with st.expander("Detalle técnico", expanded=False):
            st.write("Se usa `software/src/ejemplo_ipo.json`, con cifras inventadas solo para probar el panel.")
            st.code(resp.motivo or "Sin detalle", language=None)


def recuadro_supuestos(resp) -> None:
    with st.expander("Supuestos y fuentes (leídos de la respuesta del IPO)", expanded=True):
        d = resp.datos
        f = d["factor_plantas_a_toneladas"]
        st.markdown(
            f"**Escenario:** {d['escenario']} · **Factor plantas→t:** mín {f['min']} / base {f['base']} / "
            f"máx {f['max']} {f['unidad']} · **Ventana de maduración:** {d['ventana_maduracion_anios']} años"
        )
        c1, c2 = st.columns(2)
        c1.markdown("**Supuestos**\n\n" + "\n".join(f"- {s}" for s in d["supuestos"]))
        c2.markdown("**Fuentes**\n\n" + "\n".join(f"- {s}" for s in d["fuentes"]))


def df_faltante(nombre: str) -> pd.DataFrame | None:
    df = datos.cargar(nombre)
    if df is None:
        st.warning("📂 " + datos.mensaje_faltante(nombre))
    return df


def filtrar_municipio(df: pd.DataFrame | None, municipios: list[str]) -> pd.DataFrame | None:
    if df is None or not municipios:
        return df
    return df[df["municipio"].isin(municipios)]


# ---------- Barra lateral ----------
st.sidebar.title("🌵 Centinela·Agave")
escenario = st.sidebar.selectbox("Escenario", ESCENARIOS, index=1)

denue_df = datos.cargar("denue")
censo_df = datos.cargar("censo")
opciones_mun = sorted(
    set(denue_df["municipio"].dropna() if denue_df is not None else [])
    | set(censo_df["municipio"].dropna() if censo_df is not None else [])
)
municipios = st.sidebar.multiselect(
    "Municipio (solo DENUE y Censo)",
    opciones_mun,
    format_func=datos.nombre_bonito,
    placeholder="Todos" if opciones_mun else "Sin datos de municipios todavía",
    disabled=not opciones_mun,
)
st.sidebar.info(AVISO_IPO_REGIONAL)

st.title("🌵 Centinela·Agave")
st.markdown("**Cuánto agave madurará cada año frente a lo que la industria del tequila puede absorber.** "
            "Cuenta plantas con visión por computadora, calcula el Índice de Presión de Oferta (IPO) y lo pone junto a "
            "los datos oficiales de Jalisco (DENUE, exportaciones y Censo Económico).")
tab_conteo, tab_calendario, tab_ipo = st.tabs(["1 · Conteo de plantas", "2 · Calendario de madurez", "3 · IPO y contexto"])

# ---------- 1. Conteo de plantas ----------
with tab_conteo:
    st.subheader("Conteo de plantas")
    st.caption("El modelo se entrenó con imágenes aéreas; en fotos de ángulo bajo o con plantas muy juntas puede contar de menos. "
               "Ajusta la confianza mínima para explorar.")
    archivo = st.file_uploader("Sube una imagen o un video", type=["jpg", "jpeg", "png", "mp4", "mov", "avi"])
    vision, motivo = cargar_modulo_vision()
    if vision is None:
        st.warning(f"⚠️ **RESULTADO DE EJEMPLO** — el módulo de visión no está disponible ({motivo}).")

    if archivo is not None:
        sufijo = Path(archivo.name).suffix.lower()
        es_video = sufijo in {".mp4", ".mov", ".avi"}
        if vision is None:  # respaldo: solo si falló la importación
            if es_video:
                st.video(archivo)
            else:
                st.image(archivo, caption="Imagen subida (sin detección)")
            st.metric("Plantas detectadas (EJEMPLO, no es una detección real)", 12)
        elif es_video and not hasattr(vision, "procesar_video"):
            st.error("El módulo de visión no define `procesar_video()`.")
        else:
            # `procesar_video` usa conf fija (0.25); el umbral solo aplica a imágenes.
            conf = 0.25 if es_video else st.slider("Confianza mínima", 0.05, 0.95, 0.25, 0.05)
            try:
                res = inferir(archivo.getvalue(), sufijo, es_video, conf)
            except Exception as e:  # imagen ilegible, pesos ausentes, video sin FPS...
                st.error(f"Falló la inferencia: {type(e).__name__}: {e}")
            else:
                if es_video:
                    mostrar_resultado_video(res)
                else:
                    mostrar_resultado_imagen(res)
    else:
        st.metric("Plantas detectadas", "—", help="Sube una imagen o un video para ver el conteo.")
        st.caption("Sube un archivo para ver el conteo.")

# ---------- 2. Calendario de madurez ----------
with tab_calendario:
    st.subheader("Calendario de madurez")
    resp = ipo_cacheado(escenario)
    aviso_ejemplo_ipo(resp)
    tarjetas_ipo(resp)
    serie = pd.DataFrame(resp.datos["serie"])

    # Dos gráficas apiladas que comparten el eje X (sin ejes duplicados).
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.16, row_heights=[0.5, 0.5],
        subplot_titles=("Oferta madura vs demanda (millones de t)", "IPO por año con banda de incertidumbre"),
    )
    # Arriba: oferta madura (barras) y demanda (línea).
    fig.add_bar(x=serie["anio"], y=serie["oferta_madura_t"] / 1e6, name="Oferta madura", marker_color=VERDE, opacity=0.65,
                hovertemplate="Oferta madura: %{y:.2f} millones de t<extra></extra>", row=1, col=1)
    fig.add_scatter(x=serie["anio"], y=serie["demanda_t"] / 1e6, mode="lines+markers", name="Demanda",
                    line=dict(color="#F2C14E", width=3), hovertemplate="Demanda: %{y:.2f} millones de t<extra></extra>", row=1, col=1)
    # Abajo: banda ipo_min–ipo_max con relleno suave, línea del IPO y referencia IPO = 1.
    fig.add_scatter(x=serie["anio"], y=serie["ipo_max"], mode="lines", line=dict(width=0), showlegend=False,
                    hoverinfo="skip", row=2, col=1)
    fig.add_scatter(x=serie["anio"], y=serie["ipo_min"], mode="lines", line=dict(width=0), fill="tonexty",
                    fillcolor="rgba(214, 39, 40, 0.18)", name="Banda del IPO (mín–máx)", hoverinfo="skip", row=2, col=1)
    fig.add_scatter(x=serie["anio"], y=serie["ipo"], mode="lines+markers", line=dict(color="#d62728", width=3), name="IPO",
                    hovertemplate="IPO: %{y:.2f}<extra></extra>", row=2, col=1)
    fig.add_hline(y=1.0, line_dash="dot", line_color="gray", annotation_text="IPO = 1 (equilibrio)",
                  annotation_position="top left", row=2, col=1)
    # Ejes con 10% de margen sobre los datos (desde 0) para que nada se corte; el del IPO incluye siempre 1.0.
    tope_oferta, tope_ipo = rangos_calendario(serie)
    fig.update_yaxes(title_text="Millones de t", range=[0, tope_oferta], row=1, col=1)
    fig.update_yaxes(title_text="IPO (oferta ÷ demanda)", range=[0, tope_ipo], row=2, col=1)
    fig.update_xaxes(dtick=1, showticklabels=True, row=1, col=1)
    fig.update_xaxes(title_text="Año", dtick=1, row=2, col=1)
    fig.update_layout(height=720, legend=LEYENDA_ARRIBA, margin=dict(t=110), hovermode="x unified")
    st.plotly_chart(fig, width="stretch")
    st.caption("La banda sombreada sale de la incertidumbre del factor plantas→toneladas (`ipo_min` a `ipo_max`).")
    recuadro_supuestos(resp)

# ---------- 3. IPO y contexto ----------
with tab_ipo:
    st.subheader("IPO y contexto")
    st.info(AVISO_IPO_REGIONAL)

    # IPO por escenario
    resps = {e: ipo_cacheado(e) for e in ESCENARIOS}
    if any(r.es_ejemplo for r in resps.values()):
        aviso_ejemplo_ipo(next(r for r in resps.values() if r.es_ejemplo))
    tarjetas_ipo(resps[escenario])
    fig = go.Figure()
    for e, r in resps.items():
        s = pd.DataFrame(r.datos["serie"])
        fig.add_scatter(x=s["anio"], y=s["ipo"], mode="lines+markers", name=e.capitalize() + (" (ejemplo)" if r.es_ejemplo else ""),
                        hovertemplate="%{x}: IPO %{y:.2f}<extra>" + e.capitalize() + "</extra>",
                        line=dict(width=4 if e == escenario else 2))
    fig.add_hline(y=1.0, line_dash="dot", line_color="gray", annotation_text="IPO = 1 (equilibrio)")
    fig.update_layout(height=420, yaxis_title="IPO (oferta madura ÷ demanda, sin unidad)", xaxis_title="Año",
                      xaxis=dict(dtick=1), legend=LEYENDA_ARRIBA, margin=dict(t=90),
                      title=dict(text="IPO por escenario (el elegido va más grueso)", x=0))
    st.plotly_chart(fig, width="stretch")
    recuadro_supuestos(resps[escenario])

    st.divider()
    col_a, col_b = st.columns(2)

    # Tequileras por municipio (DENUE)
    with col_a:
        st.markdown("#### Tequileras por municipio (DENUE 312144)")
        d = filtrar_municipio(df_faltante("denue"), municipios)
        if d is not None:
            if d.empty:
                st.info("Sin establecimientos para ese filtro.")
            else:
                cuenta = d.groupby("municipio").size().sort_values().rename("establecimientos").reset_index()
                st.plotly_chart(go.Figure(go.Bar(x=cuenta["establecimientos"], y=cuenta["municipio"].map(datos.nombre_bonito), orientation="h",
                                       marker_color=VERDE)).update_layout(
                    height=max(280, 22 * len(cuenta) + 70), margin=dict(t=50), xaxis_title="Establecimientos (número)",
                    title=dict(text="Establecimientos de elaboración de tequila por municipio", x=0)), width="stretch")
                coords = d.dropna(subset=["lat", "lon"])
                if not coords.empty:
                    st.map(coords, latitude="lat", longitude="lon")
                st.caption("El DENUE cuenta establecimientos, no productores agrícolas.")

    # Exportaciones (no se filtran por municipio)
    with col_b:
        st.markdown("#### Exportaciones de tequila")
        x = df_faltante("comercio")
        if x is not None and not x.empty:
            serie_x = x.groupby("periodo", as_index=False)["valor_usd"].sum()
            st.plotly_chart(go.Figure(go.Scatter(x=serie_x["periodo"], y=serie_x["valor_usd"], mode="lines", line=dict(color=VERDE),
                                         hovertemplate="%{x}: %{y:,.0f} USD<extra></extra>")).update_layout(
                height=340, yaxis_title="Valor exportado (USD)", xaxis_title="Mes (AAAA-MM)", margin=dict(t=50),
                title=dict(text="Exportaciones mensuales de tequila, México (Banxico)", x=0)), width="stretch")
            st.caption("Datos nacionales, solo tequila, valor en USD (Banxico). El filtro de municipio no aplica. "
                       "El último año es parcial.")

        # Serie de apoyo (opcional): UN Comtrade del Integrante 2. Si el archivo no existe, no se muestra nada.
        comtrade = datos.cargar("comtrade")
        if comtrade is not None and not comtrade.empty:
            anual = datos.exportaciones_comtrade_anual(comtrade)
            if anual is None:
                st.warning("`comercio_2208_90.csv` no trae las columnas esperadas (`valor_usd` y `anio` o `periodo`).")
            elif not anual.empty:
                st.markdown("##### HS 220890 (todos los destilados), UN Comtrade")
                st.plotly_chart(go.Figure(go.Bar(x=anual["anio"].astype(str), y=anual["valor_usd"], marker_color=VERDE,
                                      hovertemplate="%{x}: %{y:,.0f} USD<extra></extra>")).update_layout(
                    height=320, yaxis_title="Valor exportado (USD)", xaxis_title="Año", margin=dict(t=50),
                    title=dict(text="Exportaciones anuales de HS 220890, total mundo (UN Comtrade)", x=0)), width="stretch")
                st.caption("Serie de apoyo: incluye todos los destilados de la partida 220890, no solo tequila. "
                           "Total Mundo por año (UN Comtrade).")


    st.divider()
    # Censo
    st.markdown("#### Censo Económico 2024")
    nivel = st.radio("Nivel", ["Rama 3121 · industria de las bebidas", "Clase 312144 · elaboración de tequila"],
                     horizontal=True, label_visibility="collapsed")
    c = filtrar_municipio(df_faltante("censo" if nivel.startswith("Rama") else "censo_tequila"), municipios)
    if c is not None:
        st.info(datos.AVISO_CONFIDENCIAL)
        if c.empty:
            st.info("Sin datos del Censo para ese filtro (no todos los municipios tienen esa actividad).")
        else:
            r = datos.resumen_censo(c)

            def total(col: str, etiqueta: str, decimales: int) -> None:
                suma, n = r[col]["suma"], r[col]["n_con_dato"]
                valor = "sin dato" if suma is None else f"{suma:,.{decimales}f}"
                metricas[col].metric(etiqueta, valor, help=f"Suma de los {n} de {r['municipios']} municipios con dato; "
                                                          "los vacíos (confidenciales) no se suman.")

            metricas = dict(zip(["ue", "personal_ocupado", "produccion_bruta"], st.columns(3)))
            metricas["ue"].metric("Unidades económicas", f"{r['unidades_economicas']:,}",
                                  help=f"Suma de {r['municipios']} municipios; esta variable siempre viene completa.")
            total("personal_ocupado", "Personal ocupado", 0)
            total("produccion_bruta", "Producción bruta (millones de pesos)", 1)
            st.caption("Las sumas usan solo valores no vacíos y solo de los municipios mostrados: "
                       "**no son el total estatal** (los municipios no se pueden sumar para obtenerlo).")
            # placeholder: el navegador ignora el na_rep del Styler en celdas nulas de columnas numéricas
            # y mostraba "None". Así las celdas siguen siendo numéricas (el orden al ordenar no cambia).
            st.dataframe(
                datos.estilo_tabla_censo(c), hide_index=True, width="stretch", placeholder="—",
                column_config=columnas_tabla_censo(),
            )
            st.caption("El Censo 2024 describe el año 2023. Montos en millones de pesos a precios corrientes de 2023. "
                       "El personal ocupado del Censo no equivale a puestos de trabajo afiliados al IMSS.")

# ---------- Pie de página ----------
st.divider()
st.caption("Fuentes: DENUE (INEGI), mayo 2026 · Banxico, Cubo de Comercio Exterior · UN Comtrade, HS 220890 · "
           "Censos Económicos 2024 (INEGI) · IPO con supuestos en `ipo/SUPUESTOS.md`. "
           "Desarrollado con apoyo de Claude Code.")
