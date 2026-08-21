# RAÍZ OPENCLAW — CÓMO HACER TODO

## Propósito
Este archivo es el mapa operativo para reconstruir y trabajar con OpenClaw sin sobreingeniería, sin duplicar formatos y sin confundir código fuente con artefactos generados.

## 1. Fuente de verdad
- Repositorio oficial: `openclaw/openclaw`
- Para una versión fija, usar un tag exacto.
- Para una copia recuperable del código fuente, conservar el árbol del tag; no `node_modules`, no `dist` generado y no artefactos locales.
- Si se necesita historial, usar Git. Si solo se necesita el árbol fuente, usar el ZIP del tag.

## 2. Qué debe conservarse del árbol fuente
La raíz de una copia de OpenClaw debe conservar los directorios y archivos versionados que forman el proyecto, incluyendo cuando existan:

`.agents/`, `.claude/`, `.github/`, `.vscode/`, `apps/`, `config/`, `deploy/`, `docs/`, `examples/`, `extensions/`, `git-hooks/`, `packages/`, `patches/`, `qa/`, `scripts/`, `security/`, `skills/`, `src/`, `test/`, `ui/`.

Y los archivos de raíz versionados como `AGENTS.md`, `CHANGELOG.md`, `LICENSE`, `README.md`, `openclaw.mjs`, `package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, los `tsconfig*.json`, configuraciones de build/test y demás archivos que pertenezcan al tag elegido.

**Regla:** no inventar ni reconstruir la raíz manualmente si se puede obtener directamente del tag oficial.

## 3. Qué NO subir como código fuente
No conservar como parte de la copia de recuperación los artefactos generados o locales, por ejemplo:

- `node_modules/`
- `dist/`
- `build/`
- `coverage/`
- `.cache/`
- logs
- bases de datos locales
- archivos temporales
- credenciales y `.env` con secretos

`pnpm-lock.yaml` sí se conserva cuando está versionado por el proyecto.

## 4. Validación mínima
Antes de declarar una copia útil:

1. Confirmar versión/tag.
2. Confirmar que existe `package.json` y `pnpm-lock.yaml` cuando correspondan al tag.
3. Instalar dependencias con el gestor indicado por el proyecto.
4. Ejecutar el build oficial indicado por el proyecto.
5. Si se usa Docker, preferir el procedimiento oficial `scripts/docker/setup.sh` y una imagen oficial GHCR.
6. Registrar exactamente el resultado: PASS o FAIL y el error real.

## 5. Docker
OpenClaw documenta Docker como una opción para un Gateway aislado. El flujo oficial usa:

`./scripts/docker/setup.sh`

Para una imagen preconstruida se puede establecer `OPENCLAW_IMAGE` con una imagen oficial de GHCR antes de ejecutar el setup.

No sustituir el Dockerfile oficial por una versión simplificada sin necesidad.

## 6. Método de trabajo / recuperación
Usar siempre esta secuencia:

**DESCUBRIR → VALIDAR → CONSERVAR → PROBAR → DOCUMENTAR**

- **DESCUBRIR:** identificar tag, raíz y archivos reales.
- **VALIDAR:** comprobar que la fuente corresponde al tag elegido.
- **CONSERVAR:** guardar únicamente código y documentación necesarios.
- **PROBAR:** ejecutar una prueba reproducible y guardar su resultado.
- **DOCUMENTAR:** registrar última salida, siguiente salida y cualquier fallo.

## 7. Regla contra alucinaciones
No afirmar que algo funciona porque debería funcionar. Una operación se marca como correcta solo cuando existe evidencia real: archivo presente, commit confirmado, ejecución de CI confirmada o salida de comando verificable.

## 8. Regla de limpieza
Antes de borrar archivos de una copia de trabajo:

- hacer inventario de la raíz;
- separar documentos de recuperación de artefactos de prueba;
- conservar solo los documentos explícitamente autorizados;
- borrar pruebas y artefactos después de cerrar la auditoría;
- volver a listar la raíz y verificar que no quedaron restos.

## 9. Estado de este repositorio
Este repositorio es un repositorio de trabajo/recuperación, no una copia completa de OpenClaw. Los documentos conservados aquí sirven como bitácora, mapa de versión, recovery patch y método de trabajo. La fuente completa de OpenClaw debe obtenerse del repositorio oficial cuando se vaya a reconstruir el motor.
