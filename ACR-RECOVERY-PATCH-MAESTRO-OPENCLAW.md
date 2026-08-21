# ACR RECOVERY PATCH MAESTRO — OPENCLAW

**Versión:** 1.1  
**Propósito:** punto único de recuperación para reconstruir, validar y desplegar OpenClaw en GitHub sin sobreingeniería, sin duplicar archivos y sin depender de memoria conversacional.

---

## 0. REGLA PRINCIPAL

Este archivo es el mapa operativo. Si el chat se reinicia, el trabajo continúa leyendo este parche y verificando GitHub.

**Nunca asumir que una operación ocurrió porque fue ordenada o descrita.** Una operación sólo queda CONFIRMADA cuando existe evidencia real en GitHub: commit, SHA/blob, archivo leído posteriormente o ejecución verificable.

Estados permitidos:

- **CONFIRMADO:** existe evidencia GitHub.
- **PENDIENTE:** se ordenó o intentó, pero falta evidencia.
- **FALLIDO:** existe evidencia de error.
- **HISTÓRICO:** pertenece a una prueba o intento anterior y no representa el estado actual.

---

# 1. OBJETIVO FINAL

El objetivo es que el usuario entregue los archivos/fuentes de OpenClaw y que el agente:

1. reciba los archivos sin modificarlos;
2. identifique exactamente qué versión/ref representan;
3. reconstruya el árbol correcto;
4. conserve todos los archivos necesarios del proyecto;
5. excluya dependencias y artefactos generados innecesarios;
6. verifique integridad antes de publicar;
7. despliegue el código al repositorio destino;
8. compruebe mediante lectura posterior que el despliegue quedó completo;
9. documente versión, commits, SHA, inventario y resultado;
10. deje un punto de recuperación reproducible para continuar posteriormente.

**No se debe intentar instalar, compilar o desplegar antes de conocer el árbol y la fuente exacta.**

---

# 2. ROLES DE LOS ARCHIVOS

## 2.1 Este parche
`ACR-RECOVERY-PATCH-MAESTRO-OPENCLAW.md`

Es el procedimiento principal.

## 2.2 Bitácora
`BITACORA-ACR-XRAY.md`

Guarda decisiones, errores, soluciones y lecciones reutilizables.

## 2.3 Mapa de versión
`ACR-VERSION-MAP.md`

Ayuda a seleccionar la fuente/ref correcto y a distinguir ramas históricas.

## 2.4 Mapa de raíz
`RAIZ-OPENCLAW-COMO-HACER-TODO.md`

Describe qué pertenece al árbol fuente y qué son artefactos locales.

## 2.5 Recovery patch anterior
`ACR-RECOVERY-PATCH-ZIP.md`

Conserva las reglas históricas de descarga/verificación mediante ZIP. No debe utilizarse para inventar un estado actual si la fuente/ref cambia.

## 2.6 Anexo de accesorios
`ACR-RECOVERY-PATCH-ANEXO-ACCESORIOS-INSTALACION.md`

Detalla qué dependencias pesadas se reconstruyen durante el build/despliegue de OpenClaw y Hermes, qué permanece en GitHub y qué NO debe subirse.

---

# 3. FUENTE DE VERDAD

Fuente oficial:

`openclaw/openclaw`

No usar forks, mirrors, paquetes de terceros ni resultados de búsquedas como sustituto de la fuente oficial salvo que se documente explícitamente una excepción.

Antes de desplegar se debe fijar:

- versión/tag, o
- commit SHA completo.

**Nunca usar `main` como versión de recuperación si se necesita reproducibilidad.**

Si el usuario entrega un ZIP/árbol, primero verificar qué ref/version representa. Si no se puede demostrar, marcar la versión como PENDIENTE y no inventarla.

---

# 4. QUÉ DEBE SUBIR EL USUARIO

El usuario puede entregar una de estas formas:

### A. ZIP de código fuente
Preferido cuando el árbol ya está preparado.

### B. Árbol de archivos
El usuario puede subir las carpetas/archivos directamente.

### C. Repositorio/ref exacto
Si existe una fuente oficial verificable, se puede reconstruir desde ella.

### D. Paquetes o artefactos adicionales
Sólo se conservan si se demuestra que son necesarios para el despliegue elegido.

**Regla:** no duplicar ZIP + TAR + copia extraída + copia recompilada sin una razón concreta.

---

# 5. CUANDO LLEGUEN LOS ARCHIVOS

Ejecutar este orden exacto:

### PASO 1 — INVENTARIO
Registrar:

- nombre del archivo;
- ruta relativa;
- tamaño;
- SHA-256 cuando sea posible;
- tipo;
- si es código fuente, documentación, configuración, dependencia o artefacto.

### PASO 2 — IDENTIFICACIÓN
Determinar:

- versión/tag;
- commit fuente si existe;
- estructura raíz;
- gestor de paquetes;
- scripts de build;
- configuración Docker;
- posibles archivos generados.

### PASO 3 — COMPARACIÓN
Comparar contra la raíz real del ref fijado.

Detectar:

- faltantes;
- extras;
- archivos modificados;
- duplicados;
- artefactos generados;
- archivos que no pertenecen al proyecto.

### PASO 4 — VALIDACIÓN
No escribir al destino hasta que el inventario sea coherente.

### PASO 5 — DESPLIEGUE
Escribir sólo los archivos autorizados.

### PASO 6 — VERIFICACIÓN POSTERIOR
Volver a leer el destino y comparar con el inventario esperado.

---

# 6. RAÍZ OPENCLAW

La raíz no se reconstruye manualmente si existe el árbol oficial del ref.

Entre los elementos que pueden formar parte de la raíz oficial están:

`.agents/`
`.claude/`
`.github/`
`.vscode/`
`apps/`
`config/`
`deploy/`
`docs/`
`examples/`
`extensions/`
`git-hooks/`
`packages/`
`patches/`
`qa/`
`scripts/`
`security/`
`skills/`
`src/`
`test/`
`ui/`

Y archivos como:

`AGENTS.md`
`CHANGELOG.md`
`LICENSE`
`README.md`
`openclaw.mjs`
`package.json`
`pnpm-lock.yaml`
`pnpm-workspace.yaml`
`tsconfig*.json`
`vitest*.config.*`
`tsdown*.config.*`

**La lista anterior es orientativa, no un inventario cerrado. El ref oficial es quien decide qué existe realmente.**

---

# 7. QUÉ NO DEBE DESPLEGARSE COMO FUENTE

Por defecto excluir:

- `node_modules/`
- `.pnpm-store/`
- `dist/`
- `build/`
- `coverage/`
- `.cache/`
- `.tmp/`
- logs;
- bases de datos locales;
- credenciales;
- `.env` con secretos;
- screenshots generados por tests;
- caches de herramientas;
- resultados temporales de CI.

No eliminar automáticamente un archivo sólo porque sea grande. Primero determinar si está versionado y si forma parte del proyecto.

**`pnpm-lock.yaml` se conserva cuando pertenece al ref oficial.**

---

# 8. LÍMITE GITHUB Y ARCHIVOS GRANDES

Antes de escribir:

1. encontrar archivos grandes;
2. identificar cuáles son fuente y cuáles son artefactos;
3. no dividir ni modificar contenido para ocultar un problema de tamaño;
4. usar Git LFS sólo si realmente existe una necesidad justificada y el proyecto lo requiere;
5. si un archivo fuente individual supera el límite permitido, detenerse y registrar la incidencia.

Un ZIP fuente no debe subirse simplemente como sustituto de su árbol si el objetivo final es tener el código navegable en GitHub.

---

# 9. DESPLIEGUE POR SEGMENTOS

Si el árbol completo no puede escribirse en una sola operación:

### Familia 01 — raíz/manifiestos
Archivos de raíz y configuración esencial.

### Familia 02 — `src/`
Código principal.

### Familia 03 — `packages/`
Paquetes internos.

### Familia 04 — `extensions/`
Extensiones.

### Familia 05 — resto del proyecto + validación
`apps/`, `ui/`, `scripts/`, `docs/`, `test/`, etc., según el inventario real.

Cada segmento debe tener:

- cursor;
- archivo actual;
- SHA fuente;
- SHA destino;
- commit destino;
- estado;
- siguiente archivo.

**No saltar de familia sin cerrar la anterior.**

---

# 10. LEDGER / CURSOR

Si existe `LEDGER.json`, es la autoridad transaccional.

Nunca continuar desde una cifra recordada del chat.

Cada escritura debe registrar conceptualmente:

```text
salida_actual
siguiente_salida
familia
ruta
sha_fuente
sha_destino
commit_destino
estado
error_si_existe
```

Si el ledger no está disponible, crear un estado de recuperación provisional y marcarlo PENDIENTE hasta que se sincronice con GitHub.

---

# 11. REGLA DE ESCRITURA

Para cada archivo:

1. comprobar si ya existe;
2. si existe, leer su SHA/contenido;
3. comparar con la fuente;
4. si coincide, marcar como ya verificado y no duplicar;
5. si difiere, registrar diferencia antes de reemplazar;
6. escribir;
7. confirmar commit/SHA devuelto por GitHub;
8. leer nuevamente el archivo;
9. confirmar que el contenido coincide;
10. avanzar al siguiente archivo.

**Nunca sobrescribir a ciegas.**

---

# 12. VALIDACIÓN TÉCNICA

Después de reconstruir el árbol, realizar las pruebas mínimas que correspondan al ref:

### Nivel 1 — integridad del árbol
- raíz completa;
- manifiestos presentes;
- lockfile presente;
- no faltan archivos versionados;
- no hay duplicados introducidos por la recuperación.

### Nivel 2 — dependencias
Usar el gestor indicado por el proyecto, por ejemplo `pnpm` cuando corresponda.

### Nivel 3 — build
Ejecutar los scripts oficiales del proyecto, no comandos inventados si existe un script documentado.

### Nivel 4 — UI
Si el proyecto contiene UI y el ref define un build específico, ejecutarlo.

### Nivel 5 — Gateway/Docker
Si se valida Docker, preferir el flujo oficial de OpenClaw y una imagen oficial de GHCR.

### Nivel 6 — smoke test
Comprobar que el proceso real arranca y responde.

**Un FAIL no se convierte en PASS cambiando la prueba sin documentar por qué.**

---

# 13. DOCKER

Cuando se utilice Docker:

1. fijar la imagen exacta;
2. comprobar que existe;
3. usar preferentemente el procedimiento oficial de OpenClaw;
4. no inventar una configuración mínima si el proyecto ya proporciona scripts oficiales;
5. guardar logs del fallo;
6. separar fallo de imagen, fallo de configuración y fallo de aplicación.

El flujo oficial documentado históricamente utiliza:

`./scripts/docker/setup.sh`

y puede trabajar con una imagen preconstruida mediante `OPENCLAW_IMAGE`.

Las pruebas anteriores A/B/C del repositorio fueron **pruebas históricas**. No deben interpretarse como prueba de que el código fuente completo esté integrado actualmente.

---

# 14. INSTALACIÓN DE ACCESORIOS Y DEPENDENCIAS PESADAS

Esta sección es obligatoria para entender la diferencia entre **fuente recuperable** y **entorno operativo generado**.

## 14.1 OpenClaw — instalación de dependencias

Desde la raíz del proyecto:

```bash
cd openclaw
pnpm install
```

Este comando lee los manifiestos del proyecto, principalmente `package.json` y `pnpm-workspace.yaml`, y resuelve/instala las dependencias declaradas en el workspace.

Entre las dependencias que pueden quedar instaladas, según el ref elegido, se encuentran componentes como:

- `sharp` para procesamiento de imágenes;
- `node-llama-cpp` para soporte de LLM local;
- SDKs e integraciones de canales como WhatsApp/Baileys, Telegram/grammY, Discord, Slack/Bolt y otros.

El resultado se materializa principalmente en:

```text
node_modules/
.pnpm-store/   # según configuración/entorno
```

Estos directorios son **artefactos del entorno de instalación** y no forman parte de la copia de recuperación que se publica en GitHub.

## 14.2 OpenClaw — UI

Si el ref elegido define el script `ui:build`:

```bash
pnpm ui:build
```

Este proceso resuelve las dependencias necesarias para la Control UI y genera los artefactos de compilación correspondientes. Puede involucrar herramientas como Vite y Lit cuando estén declaradas por la versión concreta.

## 14.3 OpenClaw — build principal

Cuando el `package.json` del ref elegido define `build`:

```bash
pnpm build
```

Puede generar `dist/` u otros directorios definidos por la versión concreta. Verificar siempre los scripts reales del `package.json` del ref fijado.

## 14.4 OpenClaw — `pnpm approve-builds`

En versiones de pnpm que bloqueen scripts de instalación que requieren aprobación, puede ser necesario revisar/aprobar los builds de dependencias.

La operación indicada históricamente en este workflow es:

```bash
pnpm approve-builds -g
```

**IMPORTANTE:** no ejecutar este comando ciegamente como requisito universal. Su comportamiento y sintaxis dependen de la versión de pnpm. Primero revisar la salida de `pnpm install` y la versión de pnpm requerida por el proyecto.

Si una dependencia queda bloqueada por scripts de build, registrar dependencia, versión de pnpm, mensaje real, aprobación necesaria y resultado.

## 14.5 Hermes — instalación completa

Si se utiliza el instalador oficial de Hermes:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

Este método puede clonar/instalar el agente y preparar su entorno según el instalador oficial vigente.

**No ejecutar este instalador dentro del repositorio OpenClaw ni mezclar sus dependencias con las de OpenClaw.**

## 14.6 Hermes — código ya presente

Si el código de Hermes ya está presente y se necesita instalar sus extras:

```bash
cd "${HERMES_HOME:-$HOME/.hermes}/hermes-agent"
uv pip install -e ".[all,dev]"
```

Este comando utiliza la configuración declarada por `pyproject.toml` y crea/usa el entorno Python correspondiente.

## 14.7 Regla repositorio vs servidor final

| Componente | GitHub | Entorno final |
|---|---|---|
| OpenClaw código fuente | SÍ | — |
| `package.json` | SÍ | — |
| `pnpm-lock.yaml` | SÍ, si está versionado | — |
| `pnpm-workspace.yaml` | SÍ | — |
| `node_modules/` | NO | `pnpm install` |
| `.pnpm-store/` | NO | según gestor/entorno |
| `dist/` generado | NO, salvo que el ref lo versione expresamente | `pnpm build` |
| UI build generado | NO, salvo que el ref lo versione expresamente | `pnpm ui:build` |
| Hermes código fuente | SÍ | — |
| `pyproject.toml` | SÍ | — |
| `.venv/` | NO | `uv pip install ...` |

La columna GitHub siempre queda subordinada al árbol real del ref elegido. Si el proyecto versiona explícitamente un artefacto, se debe conservar salvo decisión documentada.

## 14.8 Regla Dockerfile/servidor

Si el despliegue usa Docker o cualquier entorno de build reproducible, las instalaciones deben ocurrir durante el build o inicialización del entorno, no como archivos copiados desde el teléfono/PC del usuario.

Conceptualmente:

```dockerfile
# fuente ya presente en la imagen
RUN pnpm install
RUN pnpm ui:build
RUN pnpm build
```

Estas líneas son un modelo conceptual, no un Dockerfile para copiar sin revisar. Si OpenClaw proporciona un procedimiento Docker oficial, ese procedimiento tiene prioridad.

## 14.9 Regla de recuperación

Si el entorno final se pierde, NO se recuperan `node_modules` ni `.venv` desde GitHub. Se recuperan fuente exacta, versión/tag/commit, manifests, lockfiles, configuración y procedimiento de build; después se reconstruye el entorno.

## 14.10 Evidencia de instalación

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

# 15. DESPLIEGUE FINAL

Sólo cuando la validación sea suficiente:

1. congelar el inventario;
2. registrar ref/commit fuente;
3. desplegar el árbol;
4. confirmar cada familia;
5. ejecutar validación;
6. actualizar bitácora;
7. actualizar mapa de versión si cambia el ref;
8. crear commit final claramente identificado;
9. leer la raíz final;
10. generar auditoría final.

---

# 16. AUDITORÍA FORENSE FINAL

Antes de declarar TERMINADO:

### Pasada A — raíz
Listar todo el árbol final.

### Pasada B — fuente vs destino
Comparar inventario y SHA.

### Pasada C — residuos
Buscar:

- ZIPs temporales;
- archivos duplicados;
- workflows de prueba no autorizados;
- `node_modules`;
- caches;
- logs;
- archivos temporales;
- credenciales.

### Pasada D — Git
Confirmar:

- commit final;
- branch;
- archivos modificados;
- archivos eliminados;
- SHA de archivos críticos.

### Pasada E — recuperación
Comprobar que otro agente puede leer este parche y saber exactamente:

- qué fuente usar;
- qué versión usar;
- qué archivos recibió el usuario;
- qué falta;
- dónde continuar;
- cómo validar;
- qué NO debe hacer.

---

# 17. CRITERIO DE ÉXITO

El proyecto se considera **DESPLEGADO Y VERIFICADO** únicamente si:

- la fuente está fijada;
- el inventario está completo;
- el árbol destino coincide con la fuente autorizada;
- no faltan archivos necesarios;
- no se introdujeron artefactos locales indebidos;
- los commits/SHA están confirmados;
- las pruebas técnicas acordadas tienen resultado real;
- la bitácora y el mapa están sincronizados;
- existe una auditoría final reproducible.

Si cualquiera de estos puntos falla, el estado es **PENDIENTE** o **FALLIDO**, no terminado.

---

# 18. PLAN QUE SE EJECUTARÁ CUANDO EL USUARIO SUBA LOS ARCHIVOS

**ESTADO ACTUAL: ESPERANDO ARCHIVOS DEL USUARIO.**

Cuando lleguen:

`USUARIO SUBE → INVENTARIO → IDENTIFICACIÓN DE REF → VALIDACIÓN → COMPARACIÓN → DESPLIEGUE → VERIFICACIÓN → PRUEBAS → AUDITORÍA → CHECKPOINT`

El agente no debe adelantar una etapa sin evidencia de la etapa anterior.

### Última salida confirmada
El repositorio de recuperación contiene actualmente los documentos de memoria/recovery y no el árbol completo de OpenClaw.

### Siguiente salida
Recibir los archivos que el usuario va a subir, inventariarlos y fijar la fuente/version antes de comenzar el despliegue.

---

# 19. REGLAS DE NO SOBREENIGENIERÍA

- No descargar todas las releases.
- No guardar ZIP y TAR del mismo código sin motivo.
- No subir `node_modules`.
- No subir builds generados si pueden reproducirse.
- No crear infraestructura adicional sólo para demostrar que existe.
- No modificar el código fuente antes de tener una copia íntegra verificable.
- No ejecutar cinco pruebas distintas si una prueba oficial reproducible responde la pregunta.
- No borrar evidencia antes de cerrar la auditoría.
- No afirmar éxito sin evidencia.

---

# 20. RECUPERACIÓN DESPUÉS DE UN REINICIO

Un agente nuevo debe hacer:

1. leer este archivo;
2. leer `ACR-VERSION-MAP.md`;
3. leer `BITACORA-ACR-XRAY.md`;
4. comprobar GitHub directamente;
5. determinar el último commit confirmado;
6. determinar el último archivo confirmado;
7. determinar el siguiente archivo;
8. verificar que no existen dos cursores diferentes;
9. continuar sólo desde evidencia real.

**Nunca reconstruir el estado desde recuerdos del chat.**

---

# 21. FORMATO DE CHECKPOINT

Al terminar cada bloque de trabajo registrar:

```text
[CHECKPOINT]
Estado: CONFIRMADO | PENDIENTE | FALLIDO
Fuente: openclaw/openclaw@<SHA_COMPLETO>
Destino: <owner/repo>@<branch>
Familia: <familia>
Último archivo: <ruta>
SHA fuente: <sha>
SHA destino: <sha>
Commit destino: <sha>
Última salida: <qué se confirmó>
Siguiente salida: <qué toca después>
Incidencias: <ninguna o descripción>
```

Este bloque debe permitir continuar sin volver a interpretar toda la conversación.

---

# 22. PROHIBICIÓN FINAL

No borrar, mover, reemplazar ni declarar completado un componente de OpenClaw hasta que exista evidencia suficiente para saber qué es, de dónde proviene y qué función cumple.

**Fuente → evidencia → escritura → lectura posterior → validación → siguiente paso.**

---

# 23. ANEXO DE REFERENCIA

La versión ampliada y operativa de las reglas de instalación de dependencias y accesorios también queda conservada en:

`ACR-RECOVERY-PATCH-ANEXO-ACCESORIOS-INSTALACION.md`

Ese anexo sirve como referencia detallada y no reemplaza este parche maestro.
