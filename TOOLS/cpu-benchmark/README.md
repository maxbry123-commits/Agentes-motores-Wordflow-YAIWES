# CPU Benchmark Lab

Mini workflow independiente para medir el rendimiento del runner de GitHub antes de instalar OpenClaw u otros modelos/agentes.

## Diseño

- No modifica `ROOTS/openclaw/`.
- Se ejecuta únicamente en GitHub Actions.
- Las 10 pruebas se ejecutan en cadena dentro de un solo job.
- Los resultados se guardan como artifact.
- El runner estándar usado es `ubuntu-24.04`.

## Pruebas

1. Identificación de CPU
2. Sysbench CPU
3. OpenSSL SHA-256
4. 7-Zip benchmark
5. Benchmark entero compilado en C
6. Benchmark de punto flotante
7. stress-ng matrix product
8. SHA-256 sobre archivo
9. Procesamiento JSON
10. Escalado 1/2/4 hilos

## Interpretación

Los resultados son una medición del runner asignado por GitHub, no una especificación universal del procesador físico. GitHub proporciona una VM nueva para cada job de los runners estándar, por lo que se recomienda repetir el workflow para comparar variación.
