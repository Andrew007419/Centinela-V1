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

st.set_page_config(page_title="Centinela", page_icon="🌵", layout="wide")


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


def aviso_ejemplo_ipo(resp) -> None:
    if resp.es_ejemplo:
        st.warning(
            "⚠️ **DATOS DE EJEMPLO** — la API del IPO no respondió, así que estos números "
            "salen de `software/src/ejemplo_ipo.json` y **no son resultados reales**. "
            f"Detalle: {resp.motivo}",
        )


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
st.sidebar.title("🌵 Centinela")
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
    placeholder="Todos" if opciones_mun else "Sin datos de municipios todavía",
    disabled=not opciones_mun,
)
st.sidebar.info(AVISO_IPO_REGIONAL)

st.title("Centinela · presión de oferta del agave en Jalisco")
tab_conteo, tab_calendario, tab_ipo = st.tabs(["1 · Conteo de plantas", "2 · Calendario de madurez", "3 · IPO y contexto"])

# ---------- 1. Conteo de plantas ----------
with tab_conteo:
    st.subheader("Conteo de plantas")
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
        st.caption("Sube un archivo para ver el conteo.")

# ---------- 2. Calendario de madurez ----------
with tab_calendario:
    st.subheader("Calendario de madurez")
    resp = ipo_cacheado(escenario)
    aviso_ejemplo_ipo(resp)
    serie = pd.DataFrame(resp.datos["serie"])

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_bar(x=serie["anio"], y=serie["oferta_madura_t"] / 1e6, name="Oferta madura (millones t)", opacity=0.55, secondary_y=False)
    fig.add_scatter(x=serie["anio"], y=serie["ipo_max"], mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip", secondary_y=True)
    fig.add_scatter(
        x=serie["anio"], y=serie["ipo_min"], mode="lines", line=dict(width=0), fill="tonexty",
        fillcolor="rgba(214, 39, 40, 0.20)", name="Banda IPO (mín–máx)", secondary_y=True,
    )
    fig.add_scatter(x=serie["anio"], y=serie["ipo"], mode="lines+markers", line=dict(color="#d62728"), name="IPO", secondary_y=True)
    fig.add_hline(y=1.0, line_dash="dot", line_color="gray", annotation_text="IPO = 1", secondary_y=True)
    fig.update_yaxes(title_text="Oferta madura (millones de t)", secondary_y=False)
    fig.update_yaxes(title_text="IPO (oferta / demanda)", secondary_y=True)
    fig.update_xaxes(title_text="Año", dtick=1)
    fig.update_layout(height=480, legend=dict(orientation="h", y=-0.2), margin=dict(t=20))
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
    fig = go.Figure()
    for e, r in resps.items():
        s = pd.DataFrame(r.datos["serie"])
        fig.add_scatter(x=s["anio"], y=s["ipo"], mode="lines+markers", name=e + (" (ejemplo)" if r.es_ejemplo else ""),
                        line=dict(width=4 if e == escenario else 2))
    fig.add_hline(y=1.0, line_dash="dot", line_color="gray")
    fig.update_layout(height=380, yaxis_title="IPO", xaxis_title="Año", margin=dict(t=20))
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
                st.plotly_chart(go.Figure(go.Bar(x=cuenta["establecimientos"], y=cuenta["municipio"], orientation="h")).update_layout(
                    height=max(250, 22 * len(cuenta)), margin=dict(t=10), xaxis_title="Establecimientos"), width="stretch")
                coords = d.dropna(subset=["lat", "lon"])
                if not coords.empty:
                    st.map(coords, latitude="lat", longitude="lon")
                st.caption("El DENUE cuenta establecimientos, no productores agrícolas.")

    # Censo
    with col_b:
        st.markdown("#### Censo Económico 2024 · rama 3121")
        c = filtrar_municipio(df_faltante("censo"), municipios)
        if c is not None:
            if c.empty:
                st.info("Sin datos del Censo para ese filtro.")
            else:
                st.dataframe(c, hide_index=True, width="stretch")
                st.caption("Levantamiento de 2023.")

    # Exportaciones (no se filtran por municipio)
    st.markdown("#### Exportaciones de tequila")
    x = df_faltante("comercio")
    if x is not None and not x.empty:
        serie_x = x.groupby("periodo", as_index=False)["valor_usd"].sum()
        st.plotly_chart(go.Figure(go.Scatter(x=serie_x["periodo"], y=serie_x["valor_usd"], mode="lines+markers")).update_layout(
            height=320, yaxis_title="Valor (USD)", xaxis_title="Periodo", margin=dict(t=10)), width="stretch")
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
            st.plotly_chart(go.Figure(go.Bar(x=anual["anio"].astype(str), y=anual["valor_usd"])).update_layout(
                height=300, yaxis_title="Valor (USD)", xaxis_title="Año", margin=dict(t=10)), width="stretch")
            st.caption("Serie de apoyo: incluye todos los destilados de la partida 220890, no solo tequila. "
                       "Total Mundo por año (UN Comtrade).")
