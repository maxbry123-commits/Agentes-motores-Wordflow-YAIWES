# ACR Recovery Patch — OpenClaw Motor

Este archivo es el mapa visible de recuperación del proceso ACR para descargar OpenClaw como motor de Wordflow, sin la UI.

## Propósito XRAY
Este parche debe permitir que otro GPT/agente reconstruya el estado después de un reinicio sin depender de memoria conversacional. El GitHub ledger es la fuente autoritativa; el chat conserva solamente un resumen corto.

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

## Incidencias y soluciones reutilizables
- **Blob truncado:** una lectura de archivo grande puede devolver contenido incompleto. **Solución:** recuperar el blob completo o usar segmentación/reconstrucción determinista; no inventar contenido.
- **SHA equivocado:** una búsqueda puede devolver un archivo de otro commit. **Solución:** fijar el commit fuente y rechazar resultados que no pertenezcan a él.
- **Escritura parcial:** una prueba de escritura creó un fragmento de `openclaw.mjs`. **Solución:** identificar el SHA real del parcial, eliminarlo de forma controlada y reiniciar desde el blob fuente completo.
- **Escritura bloqueada:** el conector puede rechazar una operación que no garantice integridad. **Solución:** no forzar; registrar el bloqueo y cambiar a una operación exacta y verificable.
- **SHA de rama no disponible:** no mover `main` usando un SHA supuesto o truncado. **Solución:** obtener el tip completo mediante una fuente GitHub verificable antes de actualizar refs.
- **Bitácora no localizada:** búsquedas por nombre no prueban inexistencia histórica. **Solución:** auditar ramas/versiones y commits antes de crear una nueva.

## Método de auditoría de cuatro pasadas
**Pasada 1 — Chat → conocimiento:** extraer únicamente reglas, errores, soluciones y decisiones que permitan repetir o recuperar el procedimiento.

**Pasada 2 — Parche → ejecución:** comparar el mapa contra el estado real del ledger y detectar cursores, versiones, reglas o incidencias desactualizadas.

**Pasada 3 — Ledger → repositorio:** verificar que último/siguiente output, archivo exacto, SHA fuente, commit destino y familias sean coherentes.

**Pasada 4 — Recuperación:** comprobar que un agente nuevo pueda continuar usando sólo GitHub: parche + ledger + manifiestos + inventario, sin depender del chat.

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
- Branch ACR: `acr/openclaw-motor-recovery-v2`
- Fuente: `openclaw/openclaw@a4178c7eb15a0dd2b8b44804348e256f1a109a34`
- Ledger: salida 14, siguiente salida 15.
- Último archivo verificado por ledger: `.oxlintrc.json`.
- Último SHA fuente registrado: `cfa18de8e1498d7dc189daff669faca40d99881a`.
- Último commit destino registrado: `66049d58102870f9c09b828417b5764fddc6ba59`.
- Familia actual: `01-root-manifests`.
- Siguiente acción: continuar inventario raíz y no cerrar la familia hasta pasar auditoría fuente-vs-destino.

## Estado operativo de esta auditoría
- Salida de chat actual: 76.
- Se detectaron múltiples ramas históricas `acr/openclaw-motor-recovery*`; deben conservarse como evidencia hasta completar la integración y verificación.
- `main` no debe moverse usando un SHA no confirmado.
- La nueva bitácora `BITACORA-ACR-XRAY.md` debe contener únicamente información útil para recuperación/aprendizaje operativo y debe ser creada en la raíz de `main` una vez integrada la base ACR.

## Protocolo por salida
Cada salida debe dejar: número de salida, familia, segmento, fuente/ref, archivos intentados, completados, bytes transferidos, SHA fuente, commit destino, errores/reintentos, última salida, siguiente salida y siguiente archivo/segmento exacto.

## Continuación
Última salida: 76
Siguiente salida: 77 — verificar escritura de este parche y continuar con el cursor del ledger (salida 14 → 15) sin inventar progreso.
