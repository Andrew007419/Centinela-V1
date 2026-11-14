"""ETL de comercio exterior (Banxico): exportaciones de tequila, serie mensual nacional en USD.

Solo tequila (fracción 22089003 y sus subfracciones posteriores a 2021), no toda la partida 2208.90.

Entrada : data/raw/comercio*.csv   (Banxico, Cubo de Comercio Exterior, "Matriz Productos",
          formato largo con columnas Meses, TIGIE, Valor en dólares; UTF-8 con BOM)
Salida  : data/processed/comercio_tequila_banxico.csv
          (no usar el nombre comercio_2208_90.csv: ese archivo es el de UN Comtrade del Integrante 2)
Columnas: periodo (AAAA-MM), valor_usd, volumen (vacío), unidad (vacío), destino

Uso: python software/etl/comercio_2208_90.py

Regla de fracciones (la TIGIE cambió de estructura; se arma una serie continua de tequila):
  2002-04 a 2020-12 : 22089003
  2021-01 a 2021-11 : 2208909901 + 2208909992
  2021-12           : 2208900301 + 2208900391 + 2208909901
  2022-01 en adelante: 2208900301 + 2208900391
Se ignoran NA y celdas vacías. NO se suma 2208900300 (No identificado).
"""
import pandas as pd

import etl_comun as c

DESCARGA = (
    "  Banco de México, Cubo de Comercio Exterior -> 'Matriz Productos' (exportaciones, valor en dólares).\n"
    "  Descarga la matriz mensual en CSV (formato largo: Meses, TIGIE, Valor en dólares) y guárdala como\n"
    "  data/raw/comercio_2208_90.csv (o cualquier nombre que empiece con 'comercio')."
)

MESES = {m: i for i, m in enumerate(
    ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
     "septiembre", "octubre", "noviembre", "diciembre"], 1)}
DESTINO = "todas las regiones"
SALIDA = "comercio_tequila_banxico.csv"


def codigos_del_periodo(periodo: str) -> tuple[str, ...] | None:
    """Fracciones de tequila que aplican en 'AAAA-MM' (formato que ordena como texto). None si no hay regla."""
    if "2002-04" <= periodo <= "2020-12":
        return ("22089003",)
    if "2021-01" <= periodo <= "2021-11":
        return ("2208909901", "2208909992")
    if periodo == "2021-12":
        return ("2208900301", "2208900391", "2208909901")
    if periodo >= "2022-01":
        return ("2208900301", "2208900391")
    return None


def a_periodo(texto: str) -> str | None:
    """'Enero 1993' -> '1993-01'. None si no se reconoce."""
    partes = c.normalizar_texto(texto).split()
    if len(partes) == 2 and partes[0] in MESES and partes[1].isdigit():
        return f"{int(partes[1]):04d}-{MESES[partes[0]]:02d}"
    return None


def main() -> None:
    df = c.leer_csv(c.buscar_original(["comercio"], DESCARGA))
    col_mes = c.columna(df, ["meses", "mes", "periodo"], que="mes")
    col_tigie = c.columna(df, ["tigie", "fraccion", "producto"], que="fracción TIGIE")
    col_valor = c.columna(df, ["valor en dolares", "valor_usd", "valor"], que="valor en dólares")

    # El código es el primer número del texto de TIGIE ("22089003 --- Tequila"); se compara exacto.
    df = df.assign(
        _codigo=df[col_tigie].astype(str).str.extract(r"^\s*(\d+)\b", expand=False),
        _periodo=df[col_mes].map(a_periodo),
        _valor=c.a_numero(df[col_valor]),
    )
    sin_fecha = df["_periodo"].isna().sum()
    if sin_fecha:
        print(f"AVISO: {sin_fecha} filas con fecha no reconocida; se ignoran.")
    df = df[df["_codigo"].notna() & df["_periodo"].notna() & df["_valor"].notna()]  # ignora NA y vacíos

    filas = []
    for periodo, grupo in df.groupby("_periodo"):
        codigos = codigos_del_periodo(periodo)
        if codigos is None:
            continue
        usados = grupo[grupo["_codigo"].isin(codigos)]
        if usados.empty:
            print(f"AVISO: {periodo} sin datos en las fracciones {codigos}; se omite el mes.")
            continue
        filas.append({"periodo": periodo, "valor_usd": usados["_valor"].sum()})
    if not filas:
        raise c.DatosVacios("No encontré ninguna fracción de tequila en el archivo; revisa que sea la Matriz Productos de Banxico.")

    salida = pd.DataFrame(filas).sort_values("periodo")
    salida = salida.assign(volumen=None, unidad=None, destino=DESTINO)[["periodo", "valor_usd", "volumen", "unidad", "destino"]]
    print(f"Periodos: {salida.periodo.iloc[0]} a {salida.periodo.iloc[-1]}")
    c.escribir(salida, SALIDA)


if __name__ == "__main__":
    c.ejecutar(main)
