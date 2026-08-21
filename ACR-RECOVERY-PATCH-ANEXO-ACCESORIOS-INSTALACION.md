# ACR — ANEXO DEL RECOVERY PATCH
## Accesorios, dependencias y artefactos generados durante la instalación

**Versión:** ACR-RP-OPENCLAW-ADDENDUM-v1.0
**Propósito:** dejar registrado en el Recovery Patch qué comando reconstruye las dependencias pesadas de OpenClaw y Hermes, qué se conserva en GitHub y qué debe generarse únicamente durante el despliegue/build.

---

# 1. REGLA FUNDAMENTAL

El repositorio de recuperación contiene **código fuente y archivos versionados**, no `node_modules`, `.venv`, caches ni artefactos generados.

Las dependencias pesadas se reconstruyen en el entorno final de build/despliegue.

Flujo general:

```text
CÓDIGO FUENTE EN GITHUB
        ↓
BUILD / DESPLIEGUE
        ↓
INSTALACIÓN DE DEPENDENCIAS
        ↓
node_modules / .venv / artefactos
        ↓
APLICACIÓN OPERATIVA
```

Por tanto:

> **NO subir `node_modules/` ni `.venv/` al repositorio como sustituto del proceso de instalación.**

---

# 2. OPENCLAW — COMANDO QUE RECONSTRUYE LAS DEPENDENCIAS

Desde la raíz del proyecto OpenClaw:

```bash
cd openclaw
pnpm install
```

Este comando lee los manifiestos del proyecto, principalmente `package.json` y `pnpm-workspace.yaml`, y resuelve/instala las dependencias declaradas en el workspace.

Entre las dependencias que pueden quedar instaladas se encuentran componentes pesados como:

- `sharp` para procesamiento de imágenes;
- `node-llama-cpp` para soporte de LLM local, cuando esté declarado por el ref elegido;
- SDKs e integraciones de canales como WhatsApp/Baileys, Telegram/grammY, Discord, Slack/Bolt y otros, según el ref y los paquetes declarados.

El resultado se materializa principalmente en:

```text
node_modules/
.pnpm-store/   # según configuración/entorno
```

Estos directorios son **artefactos del entorno de instalación** y no forman parte de la copia de recuperación que se publica en GitHub.

---

# 3. OPENCLAW — BUILD DE LA UI

Si el ref elegido define el script `ui:build`:

```bash
pnpm ui:build
```

Este proceso instala/resuelve lo necesario para la Control UI y genera los artefactos de compilación correspondientes.

Puede involucrar herramientas como Vite y Lit cuando estén declaradas por la versión concreta.

Los artefactos generados por el build no deben confundirse con el árbol fuente.

---

# 4. OPENCLAW — BUILD PRINCIPAL

Cuando el `package.json` del ref elegido define el script `build`:

```bash
pnpm build
```

Este comando compila el proyecto y puede generar:

```text
dist/
```

u otros directorios definidos por la versión concreta.

**Regla:** no asumir que todas las versiones generan exactamente los mismos directorios. Verificar siempre los scripts reales del `package.json` del ref fijado.

---

# 5. OPENCLAW — `pnpm approve-builds`

En versiones de pnpm que bloqueen scripts de instalación que requieren aprobación, puede ser necesario revisar/aprobar los builds de dependencias.

La operación indicada históricamente en este workflow es:

```bash
pnpm approve-builds -g
```

**IMPORTANTE:** no ejecutar este comando ciegamente como requisito universal. Su comportamiento y sintaxis dependen de la versión de pnpm. Primero revisar la salida de `pnpm install` y la versión de pnpm requerida por el proyecto.

Si una dependencia queda bloqueada por scripts de build, registrar:

```text
DEPENDENCIA:
VERSIÓN DE PNPM:
MENSAJE REAL:
APROBACIÓN NECESARIA:
RESULTADO:
```

No convertir una incidencia de lifecycle scripts en una afirmación de que el proyecto está roto.

---

# 6. HERMES — INSTALACIÓN COMPLETA

Si se utiliza el instalador oficial de Hermes:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

Este método puede clonar/instalar el agente y preparar su entorno según el instalador oficial vigente.

**No ejecutar este instalador dentro del repositorio OpenClaw ni mezclar sus dependencias con las de OpenClaw.**

---

# 7. HERMES — SI YA EXISTE EL CÓDIGO

Si el código de Hermes ya está presente en el fork/directorio correspondiente y se necesita instalar sus extras:

```bash
cd "${HERMES_HOME:-$HOME/.hermes}/hermes-agent"
uv pip install -e ".[all,dev]"
```

Este comando utiliza la configuración declarada por el proyecto Python (`pyproject.toml`) y crea/usa el entorno Python correspondiente.

El equivalente conceptual respecto a OpenClaw es:

```text
OpenClaw → pnpm install → node_modules/
Hermes   → uv pip install → .venv/entorno Python
```

---

# 8. REGLA DE REPOSITORIO VS SERVIDOR FINAL

| Componente | Se conserva en GitHub | Se reconstruye en el entorno final |
|---|---|---|
| OpenClaw código fuente | SÍ | — |
| `package.json` | SÍ | — |
| `pnpm-lock.yaml` | SÍ, si está versionado | — |
| `pnpm-workspace.yaml` | SÍ | — |
| `node_modules/` | NO | `pnpm install` |
| `.pnpm-store/` | NO | según el gestor/entorno |
| `dist/` generado | NO, salvo que el ref/proyecto lo versionara expresamente | `pnpm build` |
| UI build generado | NO, salvo que el ref lo versionara expresamente | `pnpm ui:build` |
| Hermes código fuente | SÍ | — |
| `pyproject.toml` | SÍ | — |
| `.venv/` | NO | `uv pip install ...` |

**Nota:** la columna de "se conserva" siempre queda subordinada al árbol real del ref elegido. Si el proyecto versiona explícitamente un artefacto, debe conservarse salvo decisión documentada.

---

# 9. REGLA PARA EL DOCKERFILE / SERVIDOR

Si el despliegue usa Docker o cualquier entorno de build reproducible, las instalaciones deben ocurrir durante el build o inicialización del entorno, no como archivos copiados desde el teléfono/PC del usuario.

Conceptualmente:

```dockerfile
# fuente ya presente en la imagen
RUN pnpm install
RUN pnpm ui:build
RUN pnpm build
```

Pero **no copiar estas líneas literalmente** sin revisar el Dockerfile y los scripts oficiales del ref seleccionado.

Si OpenClaw proporciona un procedimiento Docker oficial, ese procedimiento tiene prioridad sobre un Dockerfile inventado.

---

# 10. REGLA DE RECUPERACIÓN

Si el entorno final se pierde, NO se recuperan `node_modules` ni `.venv` desde GitHub.

Se recupera:

```text
1. fuente exacta
2. versión/tag/commit
3. manifests
4. lockfiles
5. configuración
6. Docker/procedimiento de build
```

y se reconstruye:

```text
pnpm install
pnpm ui:build   # si corresponde
pnpm build      # si corresponde
```

o, para Hermes:

```text
uv pip install -e ".[all,dev]"
```

según el proyecto y el entorno elegido.

---

# 11. REGLA CONTRA SOBREENIGENIERÍA

No descargar previamente gigabytes de dependencias para subirlos a GitHub.

No convertir `node_modules` o `.venv` en parte del código fuente.

No duplicar paquetes si el lockfile ya permite reconstruirlos.

No ejecutar un comando de instalación antes de fijar la versión/ref del código.

No declarar que una dependencia está presente hasta comprobar el resultado real del instalador.

---

# 12. PROCEDIMIENTO QUE USARÁ EL AGENTE

Cuando el usuario suba los archivos:

```text
INVENTARIO
   ↓
FIJAR REF/VERSIÓN
   ↓
VALIDAR MANIFESTS Y LOCKFILES
   ↓
DESPLEGAR CÓDIGO FUENTE
   ↓
CONSTRUIR EN EL ENTORNO FINAL
   ↓
pnpm install / uv pip install
   ↓
BUILD SI CORRESPONDE
   ↓
PRUEBA FUNCIONAL
   ↓
AUDITORÍA
```

La instalación de dependencias es una **fase posterior al despliegue del código fuente**, no un motivo para subir los directorios generados al repositorio.

---

# 13. EVIDENCIA OBLIGATORIA

Para declarar que los accesorios fueron instalados correctamente registrar:

```text
PROYECTO:
VERSION/REF:
GESTOR:
VERSIÓN DEL GESTOR:
COMANDO:
RESULTADO:
DEPENDENCIAS INSTALADAS:
BUILD:
RESULTADO DEL BUILD:
PRUEBA FUNCIONAL:
RESULTADO:
```

Si falla:

```text
ESTADO: FALLIDO
PASO:
COMANDO:
ERROR REAL:
CAUSA CONFIRMADA / HIPÓTESIS:
SIGUIENTE ACCIÓN:
```

---

# 14. INTEGRACIÓN CON EL RECOVERY PATCH MAESTRO

Este documento es un **anexo operativo obligatorio** de:

`ACR-RECOVERY-PATCH-MAESTRO-OPENCLAW.md`

Debe consultarse junto con:

- `ACR-VERSION-MAP.md`
- `BITACORA-ACR-XRAY.md`
- `RAIZ-OPENCLAW-COMO-HACER-TODO.md`
- `ACR-RECOVERY-PATCH-ZIP.md`

La regla central permanece:

> **GitHub conserva la fuente reproducible; el entorno final reconstruye las dependencias y artefactos necesarios.**

---

# FIN DEL ANEXO
