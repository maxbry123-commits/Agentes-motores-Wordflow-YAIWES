# BITÁCORA ACR XRAY — historial operativo reutilizable

## Objetivo
Conservar únicamente conocimiento útil del proceso para que otro GPT/agente pueda recuperar y continuar el trabajo después de un reinicio.

## Estado de recuperación
- Branch de trabajo ACR: `acr/openclaw-motor-recovery-v2`
- Fuente fijada en el mapa ACR: `openclaw/openclaw@a4178c7eb15a0dd2b8b44804348e256f1a109a34`
- Ledger operativo: salida 14 → siguiente 15.
- Último archivo verificado por ledger: `.oxlintrc.json`.
- Último SHA fuente registrado: `cfa18de8e1498d7dc189daff669faca40d99881a`.
- Último commit destino registrado: `66049d58102870f9c09b828417b5764fddc6ba59`.
- Familia actual: `01-root-manifests`.

## Lecciones operativas del historial
1. Un reinicio de la aplicación obliga a reconstruir el estado desde GitHub, no desde memoria conversacional.
2. Cada salida es un checkpoint transaccional; no significa que una operación esté completa.
3. Nunca contar bytes, archivos o segmentos sin verificación.
4. Fijar siempre el commit fuente antes de leer archivos.
5. Verificar SHA/blob fuente y destino después de cada escritura.
6. Los archivos grandes deben recuperarse mediante segmentación determinista cuando sea necesario; nunca modificar el contenido fuente para adaptarlo al canal.
7. En una escritura fallida, identificar primero el estado real del destino; después limpiar/reintentar.
8. En cada frontera de familia o segmento comparar inventario esperado contra inventario existente y detectar faltantes/extras.
9. Una búsqueda por nombre de archivo no demuestra que un archivo nunca existió: para investigar historial hay que revisar ramas/versiones y commits.
10. Nunca actualizar `main` con un SHA supuesto, truncado o no confirmado.

## Incidencias útiles
- Blob truncado → recuperar blob completo o segmentar/reconstruir y verificar.
- SHA de otro commit → descartar; mantener ref/commit fijado.
- Escritura parcial de `openclaw.mjs` → identificar SHA real del parcial, eliminar controladamente y reiniciar desde fuente.
- Escritura bloqueada por el conector → no forzar; registrar incidencia y usar una operación verificable.
- Bitácora histórica no localizada → auditar versiones/commits antes de crear una nueva.

## Auditoría de cuatro pasadas
### 1. Chat → conocimiento
Se conservaron reglas y soluciones, no conversaciones irrelevantes.
### 2. Parche → ejecución
Se detectó que el parche tenía un cursor antiguo y faltaban reglas explícitas de auditoría de cuatro pasadas y recuperación post-reinicio.
### 3. Ledger → repositorio
El ledger confirmó salida 14, siguiente 15 y `.oxlintrc.json` como último archivo verificado.
### 4. Recuperación
El sistema debe poder continuar sólo con `ACR-RECOVERY-PATCH.md`, `ACR_OpenClaw_Recovery_Patch_XRAY_1.0.json`, `LEDGER.json` y los manifiestos/inventarios de GitHub.

## Mapa de familias
1. `01-root-manifests` → `ACR/source/root/`
2. `02-src` → `ACR/source/src/`
3. `03-packages` → `ACR/source/packages/`
4. `04-extensions` → `ACR/source/extensions/`
5. `05-validation-reconstruction` → `ACR/validation/`

## Salidas relevantes del historial conversacional
- Salidas iniciales: se estableció el método de descarga por segmentos y doble historial.
- Salidas posteriores: se exigió última salida/siguiente salida y auditoría en fronteras de segmentos.
- Salidas 52–60: búsqueda de bitácora histórica por nombres y reconocimiento de que una búsqueda nominal no basta.
- Salidas 61–64: identificación de múltiples ramas ACR y necesidad de auditoría histórica entre versiones.
- Salidas 65–72: intento de integrar ACR a `main`; se estableció la regla de no usar SHA incompleto.
- Salidas 73–76: auditoría de cuatro pasadas y actualización pendiente del parche.

## Última operación confirmada
Salida 77: `ACR-RECOVERY-PATCH.md` fue actualizado en `acr/openclaw-motor-recovery-v2`.
Commit: `632ff234df7e3dce7588e3ec031338e8b2a95f58`
Blob del parche actualizado: `a8fcc13004994b1fbbeac3d7c29a14bc4e6bc379`

## Siguiente operación
Salida 78: verificar que el parche actualizado sea recuperable desde GitHub y continuar desde `LEDGER.json` salida 14 → 15. Después, integrar a `main` únicamente cuando el SHA completo de la rama esté confirmado.

## Regla de integridad
Si una operación no devuelve evidencia verificable de GitHub, debe registrarse como pendiente, nunca como completada.
