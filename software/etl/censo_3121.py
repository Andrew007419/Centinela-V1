"""ETL del Censo Económico 2024 (SAIC, INEGI): rama 3121 y clase 312144, por municipio de Jalisco.

Entrada : data/raw/censo*.csv   (exportación del SAIC en formato largo, ver mensaje de error)
Salidas : data/processed/censo_3121_municipal.csv          (filas "Rama 3121")
          data/processed/censo_312144_tequila_municipal.csv (filas "Clase 312144")
Columnas: municipio, clave_mun, anio, produccion_bruta, valor_agregado, personal_ocupado,
          unidades_economicas, confidencial

Uso: python software/etl/censo_3121.py [--anio 2023]

Reglas:
- Las primeras líneas del archivo son metadatos; el encabezado real empieza con "Año Censal".
- Se descartan las filas estatales y "Total municipal"; solo quedan filas municipales de la rama y la clase.
- clave_mun = "14" + los 3 dígitos al inicio de Municipio ("001 Acatic" -> 14001). municipio va normalizado.
- Las celdas vacías son datos CONFIDENCIALES de INEGI: quedan vacías (NaN), nunca 0. Los ceros y los
  valores negativos que trae el origen se conservan tal cual.
- confidencial = 1 si falta alguna de produccion_bruta, valor_agregado o personal_ocupado.
- Montos en millones de pesos a precios corrientes de 2023. anio = 2023 (el Censo 2024 describe 2023).
"""
import argparse
import re

import pandas as pd

import etl_comun as c

DESCARGA = (
    "  INEGI, Censos Económicos 2024, resultados definitivos -> SAIC (Sistema Automatizado de Información Censal):\n"
    "  https://www.inegi.org.mx/programas/ce/2024/\n"
    "  Consulta Jalisco, nivel municipal, SCIAN 2023, actividades 'Rama 3121' y 'Clase 312144' con las variables\n"
    "  UE, H001A, A111A y A131A; exporta a CSV y guárdalo como data/raw/censo_3121.csv\n"
    "  (o cualquier nombre que empiece con 'censo')."
)
SALIDAS = {
    "Rama 3121": "censo_3121_municipal.csv",
    "Clase 312144": "censo_312144_tequila_municipal.csv",
}
COLUMNAS = ["municipio", "clave_mun", "anio", "produccion_bruta", "valor_agregado",
            "personal_ocupado", "unidades_economicas", "confidencial"]


def buscar_por_codigo(df: pd.DataFrame, codigo: str, que: str) -> str:
    """Columna cuyo nombre empieza con el código de variable del SAIC (UE, H001A, A111A, A131A)."""
    for col in df.columns:
        if str(col).strip().upper().startswith(codigo):
            return col
    raise c.ColumnaFaltante(f"No encontré la columna de {que} (empieza con '{codigo}'). Columnas: {list(df.columns)}")


def a_entero_si_se_puede(serie: pd.Series) -> pd.Series:
    """Int64 si todos los valores presentes son enteros (para no escribir '3726.0'); si no, float."""
    presentes = serie.dropna()
    if (presentes % 1 == 0).all():
        return serie.astype("Int64")
    return serie


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--anio", type=int, default=2023, help="año de referencia si el archivo no trae 'Año Censal'")
    args = ap.parse_args()

    df = c.leer_csv_desde_encabezado(c.buscar_original(["censo"], DESCARGA), "Año Censal")
    col_anio = c.columna(df, ["año censal", "anio censal", "anio"], obligatoria=False)
    col_ent = c.columna(df, ["entidad"], que="entidad")
    col_mun = c.columna(df, ["municipio"], que="municipio")
    col_act = c.columna(df, ["actividad económica", "actividad economica", "actividad"], que="actividad económica")
    col_ue = buscar_por_codigo(df, "UE", "unidades económicas")
    col_per = buscar_por_codigo(df, "H001A", "personal ocupado total")
    col_prod = buscar_por_codigo(df, "A111A", "producción bruta total")
    col_va = buscar_por_codigo(df, "A131A", "valor agregado censal bruto")

    df = df.dropna(subset=[col_act])  # fuera filas vacías, nota y relleno del final
    df = df.assign(_ent=df[col_ent].str.extract(r"^\s*(\d+)", expand=False),
                   _mun=df[col_mun].str.extract(r"^\s*(\d{3})\b", expand=False),
                   _nombre=df[col_mun].str.extract(r"^\s*\d{3}\s+(.*?)\s*$", expand=False))
    # Solo filas municipales de Jalisco (sin estatales ni "Total municipal").
    df = df[df["_mun"].notna() & (df["_ent"] == c.CLAVE_JALISCO)]

    for nivel, archivo in SALIDAS.items():
        sub = df[df[col_act].str.strip().str.startswith(nivel)]
        if sub.empty:
            raise c.DatosVacios(f"Ninguna fila municipal de Jalisco con actividad '{nivel}' en el archivo.")
        salida = pd.DataFrame({
            "municipio": sub["_nombre"].map(c.normalizar_municipio),
            "clave_mun": [c.construir_clave_mun(e, m) for e, m in zip(sub["_ent"], sub["_mun"])],
            "anio": c.a_numero(sub[col_anio]).astype("Int64") if col_anio else args.anio,
            "produccion_bruta": c.a_numero(sub[col_prod]),
            "valor_agregado": c.a_numero(sub[col_va]),
            "personal_ocupado": a_entero_si_se_puede(c.a_numero(sub[col_per])),
            "unidades_economicas": a_entero_si_se_puede(c.a_numero(sub[col_ue])),
        })
        # Celdas vacías = confidencial (NaN, nunca 0).
        salida["confidencial"] = salida[["produccion_bruta", "valor_agregado", "personal_ocupado"]].isna().any(axis=1).astype(int)
        if salida["clave_mun"].duplicated().any():
            raise c.DatosVacios(f"Municipios repetidos en '{nivel}': {salida.loc[salida.clave_mun.duplicated(), 'clave_mun'].tolist()}")
        c.escribir(salida.sort_values("clave_mun")[COLUMNAS], archivo)


if __name__ == "__main__":
    c.ejecutar(main)
