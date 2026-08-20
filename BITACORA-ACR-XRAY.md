# BITÁCORA ACR XRAY — historial operativo reutilizable

## Objetivo
Conservar únicamente conocimiento útil del proceso para que otro GPT/agente pueda recuperar y continuar el trabajo después de un reinicio. Esta bitácora es memoria histórica; `LEDGER.json` sigue siendo la autoridad del cursor transaccional.

## Orden obligatorio de recuperación
1. `LEDGER.json` — cursor, archivo, SHA y commit destino.
2. `ACR-RECOVERY-PATCH.md` — reglas de ejecución, integridad e incidencias.
3. `ACR-VERSION-MAP.md` — selección de branch/versión y diferencias históricas.
4. `ACR_OpenClaw_Recovery_Patch_XRAY_1.0.json` — mapa estructurado.
5. Esta bitácora — lecciones, errores y soluciones.
6. Manifiestos/inventarios — comprobar qué debe existir realmente.

## Estado operativo
- Branch ACR documentado: `acr/openclaw-motor-recovery-v2`.
- Fuente fijada: `openclaw/openclaw@a4178c7eb15a0dd2b8b44804348e256f1a109a34`.
- Ledger: salida 14 → siguiente 15.
- Último archivo verificado: `.oxlintrc.json`.
- Último SHA fuente: `cfa18de8e1498d7dc189daff669faca40d99881a`.
- Último commit destino del ledger: `66049d58102870f9c09b828417b5764fddc6ba59`.
- Familia actual: `01-root-manifests`.

## Lecciones operativas reutilizables
1. Un reinicio obliga a reconstruir el estado desde GitHub, nunca desde memoria conversacional.
2. Una salida es un checkpoint de trabajo, no prueba de que una operación terminó.
3. Nunca contar bytes, archivos o segmentos sin verificación.
4. Fijar commit/ref antes de leer fuentes.
5. Verificar SHA/blob fuente y destino después de cada escritura.
6. Para archivos grandes usar segmentación determinista sólo cuando sea necesaria; jamás alterar el contenido fuente para adaptarlo al canal.
7. Tras una escritura fallida, inspeccionar primero el estado real del destino; después limpiar/reintentar.
8. En cada frontera de familia/segmento comparar inventario esperado contra inventario existente y detectar faltantes/extras.
9. Una búsqueda por nombre no demuestra inexistencia histórica; para historial revisar ramas, versiones y commits.
10. Nunca actualizar `main` con un SHA supuesto, truncado o no confirmado.
11. Separar siempre **estado confirmado**, **estado pendiente** e **hipótesis histórica**.
12. Al cambiar de versión/branch, volver a validar ledger, commit fuente y SHA antes de continuar.

## Incidencias → solución
- **Blob truncado:** recuperar blob completo o segmentar/reconstruir determinísticamente y verificar.
- **SHA de otro commit:** descartar; mantener ref/commit fijado.
- **Escritura parcial de `openclaw.mjs`:** identificar SHA real del parcial, eliminar controladamente y reiniciar desde fuente.
- **Escritura bloqueada:** no forzar; registrar incidencia y usar una operación exacta y verificable.
- **SHA de rama no disponible:** no mover refs; obtener el tip completo por una fuente GitHub verificable.
- **Bitácora histórica no localizada:** auditar versiones/commits antes de concluir que nunca existió.
- **Documentos desincronizados:** no continuar con dos cursores distintos; sincronizar parche, bitácora, mapa y ledger y registrar el commit de cada actualización.

## Auditoría de cuatro pasadas
### Pasada 1 — Chat → conocimiento
Extraer sólo reglas, errores, soluciones y decisiones que puedan repetirse. Eliminar conversación irrelevante.

### Pasada 2 — Parche → ejecución
Comparar reglas del parche con el estado real del ledger. Buscar cursores antiguos, reglas faltantes y procedimientos que no tengan criterio de verificación.

### Pasada 3 — Ledger → repositorio
Comprobar que salida, siguiente salida, archivo, SHA fuente, commit destino y familia sean coherentes. Un número de salida sin evidencia GitHub no confirma una operación.

### Pasada 4 — Recuperación independiente
Simular que un agente nuevo no conoce el chat. Debe poder elegir branch, recuperar el cursor, saber qué archivo sigue, evitar duplicados y validar el resultado usando sólo los documentos del repositorio.

## Mapa de familias
1. `01-root-manifests` → `ACR/source/root/`
2. `02-src` → `ACR/source/src/`
3. `03-packages` → `ACR/source/packages/`
4. `04-extensions` → `ACR/source/extensions/`
5. `05-validation-reconstruction` → `ACR/validation/`

## Mapa de versiones
La lista y el propósito de las ramas históricas están consolidados en `ACR-VERSION-MAP.md`. No asumir que la versión numéricamente mayor es la correcta: seleccionar por contenido, ledger y SHA verificables.

## Estado vs. afirmación histórica
- **Confirmado:** existe evidencia GitHub de la operación.
- **Pendiente:** se planificó o intentó, pero falta evidencia suficiente.
- **Histórico/hipótesis:** se menciona en el chat o en una rama histórica, pero aún no se ha demostrado con el repositorio actual.
Nunca convertir pendiente o hipótesis en confirmado.

## Historial conversacional útil
- Se estableció descarga por segmentos y doble historial.
- Se exigió registrar última salida/siguiente salida y auditar cada frontera.
- Salidas 52–60: se investigó la bitácora histórica y se estableció que una búsqueda nominal no basta.
- Salidas 61–64: se identificaron múltiples ramas ACR y se decidió auditar versiones/commits.
- Salidas 65–72: se intentó integrar ACR a `main`; se estableció la prohibición de usar SHA incompleto.
- Salidas 73–77: auditoría de cuatro pasadas y actualización verificable del parche.
- Salida 78: se identificaron tres mejoras necesarias: mapa de versiones, separación explícita de estado vs. historial y puntos de recuperación sincronizados.

## Escrituras confirmadas relevantes
- `ACR-RECOVERY-PATCH.md` actualizado en `acr/openclaw-motor-recovery-v2`.
  - Commit: `632ff234df7e3dce7588e3ec031338e8b2a95f58`
  - Blob: `a8fcc13004994b1fbbeac3d7c29a14bc4e6bc379`
- `BITACORA-ACR-XRAY.md` existe en la raíz de `main`.
- `ACR-VERSION-MAP.md` creado en la raíz de `main`.
  - Commit: `649d9f68725f240fea3b8a06503d72adcc8b63ed`

## Pendientes reales
- Integrar/verificar todo el material ACR en `main` mediante SHA completo; no declarar la integración antes de comprobarla.
- Sincronizar, si procede, el parche y los documentos de memoria con el mismo estado de integración.
- Continuar descarga desde el cursor real del ledger: salida 14 → 15.

## Regla de integridad
Si una operación no devuelve evidencia verificable de GitHub, registrarla como pendiente. No inventar progreso, bytes, commits, SHA ni archivos completados.
