"""ETL del Censo Económico 2024: rama SCIAN 3121 (industria de las bebidas), municipios de Jalisco.

Entrada : data/raw/censo*.csv   (descarga de los Censos Económicos 2024, ver mensaje de error)
Salida  : data/processed/censo_3121_municipal.csv
Columnas: municipio, clave_mun, anio, produccion_bruta, valor_agregado, personal_ocupado

Uso: python software/etl/censo_3121.py [--anio 2023]
`anio` es el año de referencia del levantamiento (el Censo 2024 mide 2023, ver data/README.md);
si el archivo trae columna de año, se usa esa.
"""
import argparse

import pandas as pd

import etl_comun as c

DESCARGA = (
    "  Censos Económicos 2024 (INEGI) -> https://www.inegi.org.mx/programas/ce/2024/\n"
    "  Descarga la tabla municipal de Jalisco con la rama 3121 en CSV (producción bruta total,\n"
    "  valor agregado censal bruto y personal ocupado total) y guárdala como data/raw/censo_3121.csv\n"
    "  (o cualquier nombre que empiece con 'censo')."
)
RAMA = "3121"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--anio", type=int, default=2023, help="año de referencia si el archivo no lo trae")
    args = ap.parse_args()

    df = c.leer_csv(c.buscar_original(["censo"], DESCARGA))

    col_rama = c.columna(df, ["rama", "codigo_act", "scian", "codigo"], que="rama SCIAN")
    col_mun = c.columna(df, ["municipio", "nom_mun", "nombre_municipio"], que="municipio")
    col_prod = c.columna(df, ["produccion_bruta", "produccion bruta total", "a111a", "pbt"], que="producción bruta")
    col_va = c.columna(df, ["valor_agregado", "valor agregado censal bruto", "a131a", "vacb"], que="valor agregado")
    col_per = c.columna(df, ["personal_ocupado", "personal ocupado total", "h001a", "poto"], que="personal ocupado")
    col_anio = c.columna(df, ["anio", "año", "year"], obligatoria=False)
    col_ent = c.columna(df, ["cve_ent", "clave_entidad", "ent"], obligatoria=False)
    col_cmun = c.columna(df, ["cve_mun", "clave_municipio", "mun"], obligatoria=False)
    col_clave = c.columna(df, ["clave_mun", "cve_geo", "cvegeo"], obligatoria=False)
    if not (col_ent and col_cmun) and not col_clave:
        c.columna(df, ["cve_ent"], que="clave de entidad y municipio (cve_ent + cve_mun)")

    # Filtro del README: rama 3121 y Jalisco.
    df = df[df[col_rama].astype(str).str.strip() == RAMA]
    if col_ent and col_cmun:
        claves = [c.construir_clave_mun(e, m) for e, m in zip(df[col_ent], df[col_cmun])]
    else:
        claves = [c.clave_desde_completa(v) for v in df[col_clave]]
    df = df.assign(_clave=pd.Series(claves, index=df.index, dtype="object"))
    df = df[df["_clave"].str.startswith(c.CLAVE_JALISCO)]
    if df.empty:
        raise c.DatosVacios(f"Ninguna fila de Jalisco con la rama {RAMA} en el archivo; revisa que sea la tabla municipal de Jalisco.")

    salida = df.assign(
        municipio=df[col_mun].map(c.normalizar_municipio),
        clave_mun=df["_clave"],
        anio=c.a_numero(df[col_anio]).astype("Int64") if col_anio else args.anio,
        produccion_bruta=c.a_numero(df[col_prod]),
        valor_agregado=c.a_numero(df[col_va]),
        personal_ocupado=c.a_numero(df[col_per]),
    )[["municipio", "clave_mun", "anio", "produccion_bruta", "valor_agregado", "personal_ocupado"]]
    c.escribir(salida, "censo_3121_municipal.csv")


if __name__ == "__main__":
    c.ejecutar(main)
