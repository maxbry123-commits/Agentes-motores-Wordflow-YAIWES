# Parte 05 — validación y reconstrucción

Después de transferir las partes 01–04:

1. verificar rutas y hashes;
2. confirmar ausencia de `ui/**`;
3. confirmar ausencia de dependencias instaladas/cachés;
4. reconstruir el árbol fuente;
5. instalar dependencias con pnpm en el entorno de ejecución;
6. ejecutar build del motor, no el build de UI;
7. registrar resultado y checksums finales.

Prioridad: CRÍTICA

Esta parte no contiene el código de OpenClaw: contiene los controles que impiden declarar completa una recuperación incompleta o corrupta.
