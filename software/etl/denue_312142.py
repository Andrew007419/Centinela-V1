"""ETL del DENUE: clase SCIAN 312142 (elaboración de bebidas destiladas de agave), Jalisco.

Entrada : data/raw/denue*.csv   (descarga del DENUE, ver mensaje de error)
Salida  : data/processed/denue_312142_jalisco.csv
Columnas: nombre, municipio, clave_mun, lat, lon, estrato_personal

Uso: python software/etl/denue_312142.py [--clase 312142]
El archivo original puede ser el DENUE completo de Jalisco (todas las actividades); se filtra aquí.
"""
import argparse

import pandas as pd

import etl_comun as c

DESCARGA = (
    "  DENUE (INEGI) -> https://www.inegi.org.mx/app/mapa/denue/ (sección 'Descarga').\n"
    "  Descarga los datos de Jalisco con actividad 312142 en formato CSV y guárdalos como\n"
    "  data/raw/denue_312142.csv (o cualquier nombre que empiece con 'denue')."
)
CLASE = "312142"  # clase indicada en software/README.md


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--clase", default=CLASE, help="código SCIAN a conservar (por defecto %(default)s)")
    clase = ap.parse_args().clase

    df = c.leer_csv(c.buscar_original(["denue"], DESCARGA))

    col_act = c.columna(df, ["codigo_act", "codigo_actividad", "scian", "clase_actividad"], que="clase SCIAN")
    col_nombre = c.columna(df, ["nom_estab", "nombre", "nombre_establecimiento"], que="nombre del establecimiento")
    col_mun = c.columna(df, ["municipio", "nom_mun"], que="municipio")
    col_lat = c.columna(df, ["latitud", "lat"], que="latitud")
    col_lon = c.columna(df, ["longitud", "lon"], que="longitud")
    col_est = c.columna(df, ["per_ocu", "estrato_personal", "estrato"], que="estrato de personal")
    col_ent = c.columna(df, ["cve_ent", "clave_entidad"], obligatoria=False)
    col_cmun = c.columna(df, ["cve_mun", "clave_municipio"], obligatoria=False)
    col_clave = c.columna(df, ["clave_mun", "cve_geo", "cvegeo"], obligatoria=False)
    if not (col_ent and col_cmun) and not col_clave:
        c.columna(df, ["cve_ent"], que="clave de entidad y municipio (cve_ent + cve_mun)")

    # Filtro del README: clase SCIAN y Jalisco. Todo se compara como texto.
    todo = df
    df = df[df[col_act].str.strip() == clase]
    if col_ent and col_cmun:
        claves = [c.construir_clave_mun(e, m) for e, m in zip(df[col_ent], df[col_cmun])]
    else:
        claves = [c.clave_desde_completa(v) for v in df[col_clave]]
    df = df.assign(_clave=pd.Series(claves, index=df.index, dtype="object"))
    df = df[df["_clave"].str.startswith(c.CLAVE_JALISCO)]
    if df.empty:
        similares = todo[todo[col_act].str.startswith(clase[:4], na=False)]
        detalle = similares.groupby([col_act, "nombre_act"] if "nombre_act" in similares else [col_act]).size()
        lista = detalle.to_string() if len(detalle) else "  (ninguno)"
        raise c.DatosVacios(
            f"Ningún establecimiento de Jalisco con codigo_act == {clase} en {len(todo)} filas.\n"
            f"Códigos que empiezan con {clase[:4]} en el archivo:\n{lista}\n"
            "Si la clase correcta es otra, corre de nuevo con --clase <código>."
        )

    salida = df.assign(
        nombre=df[col_nombre].str.strip(),
        municipio=df[col_mun].map(c.normalizar_municipio),
        clave_mun=df["_clave"],
        lat=c.a_numero(df[col_lat]),
        lon=c.a_numero(df[col_lon]),
        estrato_personal=df[col_est].str.strip(),
    )[["nombre", "municipio", "clave_mun", "lat", "lon", "estrato_personal"]]
    c.escribir(salida, "denue_312142_jalisco.csv")


if __name__ == "__main__":
    c.ejecutar(main)
