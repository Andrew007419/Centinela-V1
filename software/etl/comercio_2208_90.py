"""ETL de comercio exterior: partida 2208.90 (tequila), exportaciones de Jalisco.

Entrada : data/raw/comercio*.csv   (exportación de DataMéxico, ver mensaje de error)
Salida  : data/processed/comercio_2208_90.csv
Columnas: periodo, valor_usd, volumen, unidad, destino

Uso: python software/etl/comercio_2208_90.py
Si el archivo trae columna de producto o de estado, se filtra por 2208.90 y Jalisco;
si no la trae, se asume que la descarga ya venía filtrada y se avisa.
"""
import etl_comun as c

DESCARGA = (
    "  DataMéxico (Secretaría de Economía) -> https://www.economia.gob.mx/datamexico/\n"
    "  Busca el producto 2208.90 (SA 220890), estado Jalisco, exportaciones; descarga la serie\n"
    "  con país de destino en CSV y guárdala como data/raw/comercio_2208_90.csv\n"
    "  (o cualquier nombre que empiece con 'comercio')."
)


def main() -> None:
    df = c.leer_csv(c.buscar_original(["comercio"], DESCARGA))

    col_periodo = c.columna(df, ["periodo", "month", "mes", "year", "anio", "trimestre", "quarter"], que="periodo")
    col_valor = c.columna(df, ["valor_usd", "trade value", "valor", "valor comercial", "exportaciones"], que="valor en USD")
    col_vol = c.columna(df, ["volumen", "volume", "cantidad", "peso"], obligatoria=False)
    col_uni = c.columna(df, ["unidad", "unit", "unidad_medida"], obligatoria=False)
    col_dest = c.columna(df, ["destino", "pais", "country", "pais_destino"], obligatoria=False)
    col_prod = c.columna(df, ["producto", "product", "hs6", "hs", "partida", "fraccion"], obligatoria=False)
    col_edo = c.columna(df, ["estado", "state", "entidad"], obligatoria=False)

    if col_prod:
        df = df[df[col_prod].astype(str).str.replace(r"\D", "", regex=True).str.startswith("220890")]
    else:
        print("AVISO: el archivo no trae columna de producto; asumo que ya es la partida 2208.90.")
    if col_edo:
        df = df[df[col_edo].map(c.normalizar_texto) == "jalisco"]
    else:
        print("AVISO: el archivo no trae columna de estado; asumo que ya es Jalisco.")
    if col_vol is None or col_uni is None:
        print("AVISO: falta volumen o unidad en el original; esas columnas quedan vacías.")

    salida = df.assign(
        periodo=df[col_periodo].str.strip(),
        valor_usd=c.a_numero(df[col_valor]),
        volumen=c.a_numero(df[col_vol]) if col_vol else None,
        unidad=df[col_uni].str.strip() if col_uni else None,
        destino=df[col_dest].str.strip() if col_dest else None,
    )[["periodo", "valor_usd", "volumen", "unidad", "destino"]]
    c.escribir(salida, "comercio_2208_90.csv")


if __name__ == "__main__":
    c.ejecutar(main)
