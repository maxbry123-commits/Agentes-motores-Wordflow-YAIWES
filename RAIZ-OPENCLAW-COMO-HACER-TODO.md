# RAÍZ OPENCLAW — CÓMO HACER TODO

## Propósito
Este archivo es el mapa operativo para reconstruir y trabajar con OpenClaw sin sobreingeniería, sin duplicar formatos y sin confundir código fuente con artefactos generados.

## 1. Fuente de verdad
- Repositorio oficial: `openclaw/openclaw`
- Para una versión fija, usar un tag o commit SHA exacto.
- Para una copia recuperable del código fuente, conservar el árbol exacto del ref; no `node_modules`, no `dist` generado y no artefactos locales.
- Si se necesita historial, usar Git. Si solo se necesita el árbol fuente, usar el ZIP del ref.

## 2. Qué debe conservarse del árbol fuente
La raíz de una copia de OpenClaw debe conservar los directorios y archivos versionados que forman el proyecto, incluyendo cuando existan:

`.agents/`, `.claude/`, `.github/`, `.vscode/`, `apps/`, `config/`, `deploy/`, `docs/`, `examples/`, `extensions/`, `git-hooks/`, `packages/`, `patches/`, `qa/`, `scripts/`, `security/`, `skills/`, `src/`, `test/`, `ui/`.

Y los archivos de raíz versionados como `AGENTS.md`, `CHANGELOG.md`, `LICENSE`, `README.md`, `openclaw.mjs`, `package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, los `tsconfig*.json`, configuraciones de build/test y demás archivos que pertenezcan al ref elegido.

**Regla:** no inventar ni reconstruir la raíz manualmente si se puede obtener directamente del ref oficial.

## 3. Qué NO subir como código fuente
No conservar como parte de la copia de recuperación los artefactos generados o locales, por ejemplo:

- `node_modules/`
- `.pnpm-store/`
- `dist/`
- `build/`
- `coverage/`
- `.cache/`
- `.tmp/`
- logs
- bases de datos locales
- archivos temporales
- credenciales y `.env` con secretos
- resultados temporales de CI

`pnpm-lock.yaml` sí se conserva cuando está versionado por el proyecto.

## 4. MÉTODO OFICIAL PARA ZIP → RAÍZ GITHUB

### 4.1 GitHub NO extrae un ZIP mediante la interfaz web
La interfaz web de GitHub permite administrar archivos, pero no existe una operación web general de “Extraer ZIP aquí”. Por tanto, **no se debe subir el ZIP esperando que GitHub lo descomprima automáticamente**.

El ZIP debe manejarse en un entorno que pueda descargar/guardar bytes binarios y extraerlos. Después se publican en GitHub los archivos resultantes, cada uno en su ruta correcta.

### 4.2 Secuencia obligatoria

```text
ZIP oficial
  ↓
verificar descarga completa
  ↓
SHA-256 + tamaño
  ↓
extraer
  ↓
identificar carpeta envolvente del ZIP
  ↓
obtener árbol relativo real
  ↓
conservar exactamente las rutas relativas
  ↓
comparar/inventariar
  ↓
escribir archivos en sus rutas GitHub
  ↓
confirmar commit/SHA
  ↓
leer nuevamente GitHub
  ↓
comparar fuente ↔ destino
```

### 4.3 Carpeta envolvente del ZIP
Los ZIP de GitHub normalmente pueden contener una carpeta superior asociada al repositorio/ref. Esa carpeta es una **envoltura de descarga**, no debe convertirse automáticamente en una carpeta adicional dentro de la raíz de recuperación.

Ejemplo:

```text
ZIP
└── openclaw-a4178c7.../
    ├── package.json
    ├── pnpm-lock.yaml
    ├── src/
    ├── packages/
    └── extensions/
```

La raíz destino, si el objetivo es desplegar el árbol del proyecto en la raíz del repositorio, debe quedar:

```text
/
├── package.json
├── pnpm-lock.yaml
├── src/
├── packages/
└── extensions/
```

**Nunca mover carpetas por intuición. Primero determinar la raíz relativa del ZIP y conservarla.**

### 4.4 Cómo se mueve un archivo en GitHub
GitHub permite cambiar la ruta/nombre de un archivo mediante la interfaz web. También se puede realizar mediante Git con:

```bash
git mv ruta/origen ruta/destino
```

seguido de commit/push.

Para la recuperación OpenClaw, no se debe usar el movimiento manual como sustituto de una extracción correcta. Lo preferido es escribir cada archivo directamente en la ruta final correcta.

### 4.5 Escritura directa mediante GitHub Contents API
La API de Contents permite crear/actualizar un archivo indicando directamente su `path`. Esto permite que, después de extraer el ZIP, por ejemplo:

```text
src/foo.ts
```

se publique directamente como:

```text
src/foo.ts
```

en el repositorio destino, sin crear una carpeta intermedia incorrecta.

Si el archivo ya existe, primero se debe leer su SHA y actualizarlo con ese SHA. **Nunca sobrescribir a ciegas.**

### 4.6 Verificación posterior
Una escritura solo se considera confirmada cuando:

1. GitHub devuelve evidencia del commit/SHA.
2. El archivo se vuelve a leer desde GitHub.
3. El contenido/ruta coincide con la fuente extraída.
4. Se actualiza la bitácora/ledger.

## 5. Validación mínima
Antes de declarar una copia útil:

1. Confirmar versión/tag/commit.
2. Confirmar que existe `package.json` y `pnpm-lock.yaml` cuando correspondan al ref.
3. Inventariar el árbol completo.
4. Comparar el árbol extraído con el ref elegido.
5. Instalar dependencias con el gestor indicado por el proyecto solo después de completar la recuperación del código fuente.
6. Ejecutar el build oficial indicado por el proyecto.
7. Si se usa Docker, preferir el procedimiento oficial `scripts/docker/setup.sh` y una imagen oficial GHCR.
8. Registrar exactamente el resultado: PASS o FAIL y el error real.

## 6. Docker
OpenClaw documenta Docker como una opción para un Gateway aislado. El flujo oficial usa:

`./scripts/docker/setup.sh`

Para una imagen preconstruida se puede establecer `OPENCLAW_IMAGE` con una imagen oficial de GHCR antes de ejecutar el setup.

No sustituir el Dockerfile oficial por una versión simplificada sin necesidad.

## 7. Método de trabajo / recuperación
Usar siempre esta secuencia:

**DESCUBRIR → INVENTARIAR → VALIDAR → EXTRAER → CONSERVAR → DESPLEGAR → VERIFICAR → PROBAR → DOCUMENTAR**

- **DESCUBRIR:** identificar fuente, ref y documentos de recuperación.
- **INVENTARIAR:** registrar nombres, rutas, tamaños, SHA y tipos.
- **VALIDAR:** comprobar que la fuente corresponde al ref elegido.
- **EXTRAER:** obtener el árbol del ZIP sin alterar sus rutas relativas.
- **CONSERVAR:** guardar únicamente código y documentación necesarios.
- **DESPLEGAR:** publicar cada archivo en su ruta final.
- **VERIFICAR:** releer GitHub y comparar contra la fuente.
- **PROBAR:** ejecutar pruebas reproducibles.
- **DOCUMENTAR:** registrar última salida, siguiente salida, commits, SHA y cualquier fallo.

## 8. Regla contra alucinaciones
No afirmar que algo funciona porque debería funcionar. Una operación se marca como correcta solo cuando existe evidencia real: archivo presente, commit confirmado, ejecución de CI confirmada o salida de comando verificable.

## 9. Regla de limpieza
Antes de borrar archivos de una copia de trabajo:

- hacer inventario de la raíz;
- separar documentos de recuperación de artefactos de prueba;
- conservar solo los documentos explícitamente autorizados;
- borrar pruebas y artefactos después de cerrar la auditoría;
- volver a listar la raíz y verificar que no quedaron restos.

## 10. Estado de este repositorio
Este repositorio es un repositorio de trabajo/recuperación. Los documentos conservados aquí sirven como bitácora, mapa de versión, recovery patch y método de trabajo. La fuente completa de OpenClaw debe obtenerse del repositorio oficial cuando se vaya a reconstruir el motor.

**Última actualización del método:** investigación del mecanismo GitHub ZIP → extracción → rutas → movimiento/escritura directa. Esta regla queda incorporada al procedimiento operativo y debe utilizarse antes de procesar cualquier ZIP.
