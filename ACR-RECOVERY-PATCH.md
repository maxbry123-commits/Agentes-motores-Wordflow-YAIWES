# ACR Recovery Patch — OpenClaw Motor

Este archivo es el mapa visible de recuperación del proceso ACR para descargar OpenClaw como motor de Wordflow, sin la UI.

## Propósito XRAY
Este parche debe permitir que otro GPT/agente reconstruya el estado después de un reinicio sin depender de memoria conversacional. `LEDGER.json` es la fuente autoritativa del cursor; este parche define el método y las reglas de integridad.

## Orden de recuperación
1. Leer `LEDGER.json`.
2. Leer este parche.
3. Leer `ACR-VERSION-MAP.md` para seleccionar la rama/versión correcta.
4. Leer `ACR_OpenClaw_Recovery_Patch_XRAY_1.0.json`.
5. Comprobar manifiestos/inventarios fuente-vs-destino.
6. Continuar sólo desde el cursor real del ledger.

## Regla de trabajo
1. Auditar raíz y manifests antes de descargar.
2. Fijar commit/ref y SHA/blob de cada archivo fuente.
3. Recuperar archivos grandes por segmentos deterministas cuando el canal limite la transferencia.
4. Nunca contar un parcial, intento o escritura no verificada como descargado.
5. Reconstruir y verificar contra el SHA/blob fuente antes de cerrar un archivo.
6. Si una escritura falla, conservarla como incidencia y obtener el SHA real del destino antes de eliminar/reintentar.
7. Después de cada transferencia registrar salida, familia, segmento, bytes reales, SHA fuente, commit destino, errores y siguiente cursor.
8. En cada frontera de familia/segmento hacer inventario fuente-vs-destino y detectar faltantes/extras antes de marcarla verificada.
9. Después de un reinicio leer primero `LEDGER.json` y este parche; nunca reconstruir el estado desde memoria del chat.
10. No sobrescribir contenido verificado sin registrar la razón y el nuevo SHA.
11. Separar siempre estado **confirmado**, **pendiente** e **histórico/hipotético**.
12. Nunca mover `main` con un SHA incompleto, supuesto o truncado.
13. Al cambiar de branch/versión, validar de nuevo commit fuente, SHA del tip, ledger y contenido antes de continuar.
14. Antes de declarar una integración completa, comparar el estado de `main` con el conjunto ACR esperado.

## Incidencias y soluciones reutilizables
- **Blob truncado:** una lectura de archivo grande puede devolver contenido incompleto. **Solución:** recuperar el blob completo o usar segmentación/reconstrucción determinista; no inventar contenido.
- **SHA equivocado:** una búsqueda puede devolver un archivo de otro commit. **Solución:** fijar el commit fuente y rechazar resultados que no pertenezcan a él.
- **Escritura parcial:** una prueba de escritura creó un fragmento de `openclaw.mjs`. **Solución:** identificar el SHA real del parcial, eliminarlo de forma controlada y reiniciar desde el blob fuente completo.
- **Escritura bloqueada:** el conector puede rechazar una operación que no garantice integridad. **Solución:** no forzar; registrar el bloqueo y cambiar a una operación exacta y verificable.
- **SHA de rama no disponible:** no mover `main` usando un SHA supuesto o truncado. **Solución:** obtener el tip completo mediante una fuente GitHub verificable antes de actualizar refs.
- **Bitácora no localizada:** búsquedas por nombre no prueban inexistencia histórica. **Solución:** auditar ramas/versiones y commits antes de crear una nueva.
- **Documentos desincronizados:** no continuar con dos cursores distintos. **Solución:** sincronizar parche/bitácora/mapa con el ledger y registrar los commits de actualización.

## Método de auditoría de cuatro pasadas
**Pasada 1 — Chat → conocimiento:** extraer únicamente reglas, errores, soluciones y decisiones que permitan repetir o recuperar el procedimiento.

**Pasada 2 — Parche → ejecución:** comparar el mapa contra el estado real del ledger y detectar cursores, versiones, reglas o incidencias desactualizadas.

**Pasada 3 — Ledger → repositorio:** verificar que último/siguiente output, archivo exacto, SHA fuente, commit destino y familias sean coherentes.

**Pasada 4 — Recuperación:** comprobar que un agente nuevo pueda continuar usando sólo GitHub: parche + ledger + mapa de versiones + mapa XRAY + manifiestos + inventario, sin depender del chat.

## Mapa de descarga
- `01-root-manifests`: `package.json`, `pnpm-workspace.yaml`, `pnpm-lock.yaml`, `openclaw.mjs`, `node-version.mjs`, `.npmrc`, configuraciones y avisos/licencias → `ACR/source/root/`
- `02-src`: `src/**` → `ACR/source/src/`
- `03-packages`: `packages/**` → `ACR/source/packages/`
- `04-extensions`: `extensions/**` → `ACR/source/extensions/`
- `05-validation-reconstruction`: material requerido para validar/reconstruir runtime/build → `ACR/validation/`

## Alcance
**Excluir:** `ui/**`, `node_modules/**`, `.pnpm-store/**`, caches, logs, secretos, configuración personal y artefactos generados.

**Preservar:** código fuente, paquetes, extensiones, manifests raíz y material requerido para runtime/build.

## Estado conocido del ledger
- Branch ACR documentado: `acr/openclaw-motor-recovery-v2`
- Fuente: `openclaw/openclaw@a4178c7eb15a0dd2b8b44804348e256f1a109a34`
- Ledger: salida 14, siguiente salida 15.
- Último archivo verificado por ledger: `.oxlintrc.json`.
- Último SHA fuente registrado: `cfa18de8e1498d7dc189daff669faca40d99881a`.
- Último commit destino registrado: `66049d58102870f9c09b828417b5764fddc6ba59`.
- Familia actual: `01-root-manifests`.
- Siguiente acción: continuar inventario raíz y no cerrar la familia hasta pasar auditoría fuente-vs-destino.

## Puntos de recuperación
Cada checkpoint debe conservar como mínimo: `salida`, `familia`, `segmento`, `archivo exacto`, `fuente/ref`, `SHA fuente`, `bytes reales`, `commit destino`, `estado`, `errores/reintentos`, `última salida`, `siguiente salida` y `siguiente archivo/segmento exacto`.

El número de salida por sí solo no demuestra una operación completada. La prueba es la evidencia verificable de GitHub.

## Estado operativo de esta guía
- Última salida conversacional documentada: 78.
- Tres mejoras de memoria/recovery implementadas: mapa de versiones, separación explícita de estados y puntos de recuperación sincronizados.
- `ACR-VERSION-MAP.md` es ahora la referencia para escoger entre ramas históricas.
- `BITACORA-ACR-XRAY.md` conserva lecciones; no sustituye el ledger.
- La integración total a `main` sigue pendiente hasta verificar SHA completo y contenido.

## Continuación
Última salida documentada: 78
Siguiente salida: 79 — verificar las tres mejoras en GitHub y continuar desde el cursor del ledger (salida 14 → 15) sin inventar progreso.
