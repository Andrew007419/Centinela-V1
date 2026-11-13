# Dataset de visión

Fuente observada: https://universe.roboflow.com/dataset-j66bo/agave-9kv5n
Licencia indicada en la captura de origen: CC BY 4.0; confirmar autor/título y conservar atribución de cada fuente. No sustituir por la licencia del código.
Workspace del fork: andrews-workspace-b6bbr. Versión exportada: 1.
Project slug del fork: pendiente de copiar del código Roboflow (sin API key).
Imágenes aéreas públicas; no se aportaron capturas propias desde el robot.

Se unificaron dos etiquetas de procedencia en clase 0: agave tras revisar ejemplos visuales, no una auditoría exhaustiva.
Exportación recibida: 4512 train, 384 val, 147 test (incluye variantes).
Se detectaron 151 nombres de origen compartidos entre splits.
Prioridad de conservación: test > val > train; se excluyeron 369 variantes de train y 28 de val.
Final: 4143 train, 356 val, 147 test; 302017 cajas conservadas en todos los splits, no plantas únicas.
Cruces por nombre de origen: 0. No garantiza independencia por parcela ni ausencia de solapamiento geográfico.
Respaldo Drive: CENTINELA_AGAVE/dataset_respaldo/agave_sin_cruces.zip.
Guardar division_por_origen.json y YAML del respaldo como evidencia.

Pendientes: negativos por split, cajas por split, autor y atribución completos, parámetros reales de aumentación de Roboflow y revisión de casi duplicados/parcelas. No afirmar que no hubo aumentación: la exportación contiene variantes.
