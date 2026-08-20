# ACR Recovery Patch — OpenClaw Motor

Este archivo es el mapa visible de recuperación del proceso ACR para descargar OpenClaw como motor de Wordflow, sin la UI.

## Propósito XRAY
Este parche permite que otro GPT/agente reconstruya el estado después de un reinicio sin depender de memoria conversacional. `LEDGER.json` es la fuente autoritativa del cursor; este parche define el método y las reglas de integridad.

## Orden de recuperación
1. Leer `ACR/recovery/LEDGER.json`.
2. Leer este parche.
3. Leer `ACR-VERSION-MAP.md` para seleccionar la rama/versión correcta.
4. Leer `ACR/recovery/ACR_OpenClaw_Recovery_Patch_XRAY_1.0.json`.
5. Leer la sección **Código operativo ACR** de este archivo y comprobar las rutas referenciadas.
6. Comprobar manifiestos/inventarios fuente-vs-destino.
7. Continuar sólo desde el cursor real del ledger.

## Código operativo ACR
Esta sección identifica explícitamente los artefactos que forman el motor operativo del procedimiento. Un agente nuevo debe comprobarlos antes de ejecutar una recuperación.

### Motor de recuperación y control
- `ACR/recovery/ACR_OpenClaw_Recovery_Patch_XRAY_1.0.json` — contrato/mapa XRAY: familias, segmentación, validación y reconstrucción.
- `ACR/recovery/LEDGER.json` — cursor autoritativo, eventos, archivos verificados, errores y siguiente acción.
- `ACR-RECOVERY-PATCH.md` — procedimiento, controles, incidencias y continuidad.
- `ACR-VERSION-MAP.md` — mapa de ramas/versiones y criterio para escoger versión.
- `BITACORA-ACR-XRAY.md` — memoria de lecciones, errores y soluciones; no sustituye al ledger.

### Código y artefactos fuente
- `ACR/source/root/` — manifests y archivos raíz recuperados.
- `ACR/source/src/` — destino de `src/**`.
- `ACR/source/packages/` — destino de `packages/**`.
- `ACR/source/extensions/` — destino de `extensions/**`.
- `ACR/validation/` — material de validación/reconstrucción runtime/build.

### Artefactos raíz críticos
- `ACR/source/root/openclaw.mjs` — launcher/runtime principal.
- `ACR/source/root/node-version.mjs` — lógica de versión Node.
- `ACR/source/root/package.json` — dependencias y scripts.
- `ACR/source/root/pnpm-workspace.yaml` — workspace.
- `ACR/source/root/pnpm-lock.yaml` — lockfile.
- `ACR/source/root/.npmrc` — configuración npm.
- `ACR/source/root/.oxlintrc.json` — linting.
- `ACR/source/root/.oxfmtrc.jsonc` — formatting.
- `ACR/source/root/.pre-commit-config.yaml` — hooks/pre-commit.

**Regla:** una ruta listada aquí no significa automáticamente que esté transferida. El estado válido lo determina el ledger mediante ruta + SHA/blob fuente + evidencia de destino.

## Inventario confirmado de la raíz de OpenClaw
Auditoría directa de `openclaw/openclaw` en `main`: la raíz contiene **61 entradas**, clasificadas como **40 archivos** y **21 directorios**. Los directorios son contenedores que se inventarían recursivamente por sus propias familias; no se deben contar como archivos transferibles.

- `ROOT_ENTRIES_TOTAL = 61`
- `ROOT_FILES_TOTAL = 40`
- `ROOT_DIRECTORIES_TOTAL = 21`
- `ROOT_FILES_VERIFIED_BY_LEDGER = 15` después de verificar `.pre-commit-config.yaml`.
- `ROOT_FILES_PENDING_BY_COUNT = 25`, sujeto a cruce definitivo por ruta + SHA contra los 40 archivos raíz.

La clasificación se basa en el tipo devuelto por la API de contenidos de GitHub (`file` frente a `dir`). El inventario debe mantenerse separado del conteo de archivos transferidos.

## Regla de trabajo
1. Auditar raíz y manifests antes de descargar.
2. Fijar commit/ref y SHA/blob de cada archivo fuente.
3. Recuperar archivos grandes por segmentos deterministas cuando el canal limite la transferencia.
4. Nunca contar un parcial, intento o escritura no verificada como descargado.
5. Reconstruir y verificar contra el SHA/blob fuente antes de cerrar un archivo.
6. Si una escritura falla, registrar la incidencia y obtener el SHA real del destino antes de eliminar/reintentar.
7. Después de cada transferencia registrar salida, familia, segmento, bytes, SHA fuente, commit destino, errores y siguiente cursor.
8. En cada frontera hacer inventario fuente-vs-destino y detectar faltantes/extras.
9. Después de un reinicio leer primero ledger y parche; nunca reconstruir desde memoria del chat.
10. No sobrescribir contenido verificado sin registrar razón y nuevo SHA.
11. Separar **confirmado**, **pendiente** e **histórico/hipotético**.
12. Nunca mover `main` con un SHA incompleto, supuesto o truncado.
13. Al cambiar branch/versión validar nuevamente commit fuente, tip, ledger y contenido.
14. Antes de declarar integración completa, comparar `main` con el conjunto ACR esperado.
15. Antes de usar código/herramienta ACR, comprobar ruta, SHA y estado en el ledger.
16. En la raíz, distinguir siempre `entries`, `files` y `directories`; nunca usar el número de entradas como número de archivos.

## Incidencias y soluciones reutilizables
- **Blob truncado:** recuperar blob completo o segmentar/reconstruir; no inventar contenido.
- **SHA equivocado:** fijar commit fuente y rechazar resultados de otro commit.
- **Escritura parcial:** identificar SHA del parcial, eliminar controladamente y reiniciar desde blob completo.
- **Escritura bloqueada:** no forzar; registrar bloqueo y usar operación exacta/verificable.
- **SHA de rama no disponible:** obtener tip completo antes de actualizar refs.
- **Bitácora no localizada:** auditar ramas/versiones/commits antes de crear otra.
- **Documentos desincronizados:** sincronizar parche/bitácora/mapa con ledger.
- **Archivo presente pero SHA diferente:** mantener pendiente hasta comprobar coincidencia con fuente fijada.
- **Inventario truncado:** dividir el inventario por directorio/familia y no cerrar el total hasta reconciliar todos los segmentos.

## Método de auditoría de cuatro pasadas
**Pasada 1 — Chat → conocimiento:** extraer reglas, errores, soluciones y decisiones reutilizables.

**Pasada 2 — Parche → ejecución:** comparar el método con el estado real del ledger.

**Pasada 3 — Ledger → repositorio:** verificar salida, archivo exacto, SHA fuente, commit destino y familia.

**Pasada 4 — Recuperación:** comprobar que un agente nuevo pueda continuar sólo con GitHub: parche + ledger + mapa + XRAY + manifiestos + inventario.

## Mapa de descarga
- `01-root-manifests` → `ACR/source/root/`
- `02-src` → `ACR/source/src/`
- `03-packages` → `ACR/source/packages/`
- `04-extensions` → `ACR/source/extensions/`
- `05-validation-reconstruction` → `ACR/validation/`

## Alcance
**Excluir:** `ui/**`, `node_modules/**`, `.pnpm-store/**`, caches, logs, secretos, configuración personal y artefactos generados.

**Preservar:** código fuente, paquetes, extensiones, manifests raíz y material requerido para runtime/build.

## Estado conocido
- Branch: `acr/openclaw-motor-recovery-v2`
- Fuente: `openclaw/openclaw@a4178c7eb15a0dd2b8b44804348e256f1a109a34`
- Raíz fuente auditada: 61 entradas = 40 archivos + 21 directorios.
- Ledger: salida 15 → siguiente 16 después de verificar `.pre-commit-config.yaml`.
- Último verificado: `.pre-commit-config.yaml`.
- Último SHA fuente: `24a3582ffc4914053a80e1a664bef3eafe355314`.
- Último commit destino: `86e87aeb9fe54a1864fdf27a6c952f0ed034c263`.
- Familia: `01-root-manifests`.
- Siguiente acción: continuar inventario raíz y no cerrar familia hasta pasar auditoría fuente-vs-destino.

## Puntos de recuperación
Cada checkpoint conserva: `salida`, `familia`, `segmento`, `archivo`, `fuente/ref`, `SHA fuente`, `bytes`, `commit destino`, `estado`, `errores/reintentos`, `última salida`, `siguiente salida` y `siguiente archivo/segmento`.

El número de salida no demuestra una operación completada; la prueba es evidencia verificable de GitHub.

## Estado operativo
- `ACR-VERSION-MAP.md` selecciona ramas históricas.
- `BITACORA-ACR-XRAY.md` conserva lecciones.
- La integración total a `main` sigue pendiente hasta verificar SHA completo y contenido.

## Continuación
Última salida documentada: 84
Siguiente salida: continuar desde ledger salida 15 → 16, completando el inventario de los 40 archivos raíz.
