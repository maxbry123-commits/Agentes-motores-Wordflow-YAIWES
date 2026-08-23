# Método de trabajo

## Procedimiento ZIP → nueva raíz

1. Localizar el ZIP exacto en el repositorio y verificar nombre, ruta, SHA y tamaño.
2. Descargar el ZIP como archivo binario; no interpretarlo como UTF-8.
3. Extraer todos los archivos y directorios a un área temporal.
4. Inventariar la extracción y detectar si existe una carpeta envolvente creada por el ZIP.
5. Crear una sola raíz nueva con el nombre solicitado.
6. Colocar dentro de esa raíz TODO el contenido extraído, quitando únicamente la carpeta envolvente si existe.
7. Mantener nombres, rutas internas y contenido sin modificaciones.
8. Comparar ZIP ↔ raíz desplegada por archivos, directorios, tamaños y SHA/contenido cuando sea posible.
9. Crear tree/commit conservando el resto del repositorio y actualizar la rama destino.
10. Verificar directamente en GitHub que la nueva raíz contiene todo el contenido esperado.

## Reglas

- ZIP original intacto salvo instrucción expresa.
- No clasificar, mover, borrar ni reescribir otros documentos durante esta tarea.
- GitHub es la fuente de verdad.
- TERMINADA solo después de la verificación cruzada.

Flujo: `ZIP → binario → extracción → inventario → nueva raíz## 5 maneras de que una AI copie un archivo de un repo GitHub a otro

### 1. **Contents API** (simple, 1 archivo)
1. `GET /repos/{src_owner}/{src_repo}/contents/{path}` → content (base64) + `sha`  
2. `PUT /repos/{dst_owner}/{dst_repo}/contents/{path}` con el mismo content  
3. Leer de nuevo el destino y **verificar** que el contenido (o el SHA del blob) coincida  

**Cuándo:** 1–pocos archivos, repos pequeños.  
**En Wordflow:** `get_file` → `write_files` / `remote_op("edit")` → `verify_file`.

---

### 2. **Git Data API** (blob → tree → commit → ref)
1. Leer blob(s) del repo origen  
2. Crear blob(s) en destino  
3. Crear tree → commit → actualizar ref de la rama (**sin force**)  
4. Verificar `head` / contenido  

**Cuándo:** varios archivos o commit atómico.  
**En Wordflow:** es el path de `apply_and_push` / `remote_ops` (PIPELINE 08).

---

### 3. **Workflow de Actions en Cuenta A** (copia automatizada)
- Job con `actions/checkout` del origen **o** `curl` a la API  
- Token del **destino** desde secret (`EXTERNAL_GH_B_TOKEN` / `EXTERNAL_GH_C_TOKEN`)  
- Escribe en B o C y falla si el verify no pasa  

**Cuándo:** copia recurrente, CI, sin agente en el medio.  
Hay acciones de Marketplace del tipo “copy file between repos”; el patrón es el mismo: read → write → check.

---

### 4. **Transfer / fork del repo completo** (no es “un archivo”)
- **Transfer ownership** o **Fork** si lo que quieres es el repo entero  
- No sirve si solo necesitas un path (ej. solo la guía)

**Cuándo:** migrar proyecto completo A→B o A→C (ya documentado en la guía).

---

### 5. **Clone local + push al destino** (máquina/CI con git)
```text
git clone origen → copiar archivo → remote destino → commit → push
```
**Cuándo:** scripts humanos o runners con git.  
Para la AI en este entorno suele ser peor que 1 o 2 (más superficie, más fallo).

---

## Análisis de lo que dice GPT

| Afirmación GPT | ¿Correcto? |
|----------------|------------|
| Método = leer fuente → escribir destino → verificar SHA | **Sí** — es el contrato canónico |
| Contents API y Git Data API (blob→tree→commit→ref) | **Sí** |
| Existe acción Marketplace de copia entre repos | **Sí** — confirma que el caso de uso es válido |
| No hay `copy_file` nativo en las tools → hay que componer API | **Sí** |
| Fuente canónica `GUIA_CUENTAS_REMOTE.md` SHA `752457f2…` | **Coherente** con lo que había en `agentes/main` en ese momento |
| Borrar copia no canónica en “Cerebro” hasta que el SHA coincida | **Bien** (fail-closed / no basura) |
| PIPELINE sin force-push | **Sí** — alineado con Wordflow |
| “No inventar que los 19 están terminados” | **Correcto** — no declarar PASS sin verify |

**Huecos / mejoras respecto a GPT:**

1. **No solo SHA del archivo de guía:** tras copiar, verificar también `path` + contenido (o blob SHA) en el **repo destino**, no solo “borré la copia mala”.  
2. **Multi-cuenta:** origen casi siempre **A** (`maxbry123-commits/agentes`); destino **B** o **C** con `token_ref` distinto (`EXTERNAL_GH_B_TOKEN` / `EXTERNAL_GH_C_TOKEN`). GPT habla de API genérica; en vuestro cableo hay que fijar `account_id` + secret.  
3. **Un archivo vs muchos:** Contents API (manera 1) para la guía; Git Data (manera 2) si el “GAP” es un lote.  
4. **Idempotencia:** si el destino ya tiene el mismo contenido, el PUT puede ser no-op o 409 según API; el verify debe aceptar “ya igual” como OK.  
5. **LOOP que propone:** GAP → solución → verificación → siguiente repo es el orden correcto; falta explicitar **evidencia** (`commit_sha` destino + read-back).

---

## Solución práctica recomendada (AI + Wordflow)

Para **un archivo** (ej. la guía):

```text
1. get_file(owner=A, repo=agentes, path=GUIA_CUENTAS_REMOTE.md)  → content + sha_src
2. write_files / Contents PUT en destino (B o C) con ese content
3. verify_file(destino, path, expect_content=content)  o comparar blob sha
4. Solo entonces marcar el GAP como cerrado
```

Eso es exactamente lo que GPT describe, más el cableo A/B/C y la evidencia de read-back. No hace falta una tool mágica `copy_file`: se compone con **read → write → verify**. → despliegue completo → comparación → commit → push → verificación`.




## Cómo debe borrar una AI un archivo duplicado en un repo

### Regla
**Identificar el canónico → borrar solo el duplicado → verificar que ya no existe.**  
Nunca borrar a ciegas ni el archivo “bueno”.

---

### Pasos (orden fijo)

1. **Listar / localizar duplicados**  
   - `list_tree` o Contents API  
   - Criterio: mismo nombre en otra ruta, o mismo contenido (hash) en dos paths  

2. **Elegir cuál se queda**  
   - Canónico = el de la ruta oficial (ej. raíz `GUIA_CUENTAS_REMOTE.md`)  
   - Duplicado = copia en otra carpeta (ej. `Cerebro/...`, `tmp/...`)  

3. **Borrar solo el path duplicado**  
   - **Contents API:** `DELETE /repos/{owner}/{repo}/contents/{path}` con el `sha` actual del archivo  
   - **Wordflow:** `delete_paths` / `remote_op("delete", paths=["ruta/del/duplicado"])`  
   - Token del dueño del repo (`EXTERNAL_GH_B_TOKEN` si es B, etc.)  
   - Sin force-push; un commit normal de borrado  

4. **Verificar**  
   - `get_file` / `verify_file(..., expect_missing=True)` en el path borrado → debe fallar lectura / 404  
   - Confirmar que el canónico **sigue** existiendo  

5. **Solo entonces** cerrar el GAP (con evidencia: `commit_sha` + “path X missing, path Y ok”)

---

### Ejemplo mínimo (Wordflow)

```python
# 1) Canónico OK
remote_op("read", owner="...", repo="...", path="GUIA_CUENTAS_REMOTE.md", token=token)

# 2) Borrar duplicado
remote_op("delete", owner="...", repo="...", paths=["Cerebro/GUIA_CUENTAS_REMOTE.md"], token=token, dry_run=False)

# 3) Verify
remote_op("verify_file", owner="...", repo="...", path="Cerebro/GUIA_CUENTAS_REMOTE.md",
          token=token, expect_missing=True)
```

---

### Fail-closed (no hacer)

| Situación | Acción |
|-----------|--------|
| No sabes cuál es el canónico | **No borrar**; reportar paths |
| Path protegido (workflows, secrets, etc.) | **HOLD** — no borrar |
| Sin token / dry-run | No declarar borrado real |
| Borraste sin verify | No marcar PASS |

---

### Resumen en una línea
**La AI borra el path duplicado con DELETE/Contents o `delete_paths`, comprueba que ese path ya no existe y que el canónico sigue, y solo entonces cierra el trabajo.**

Sí. La mejoro para que funcione como plantilla universal operativa para un agente de IA trabajando sobre GitHub, con memoria persistente en PIPELINE + BITÁCORA, ejecución por lotes, LOOP continuo, resolución de GAPs y verificación cruzada.

PLANTILLA UNIVERSAL — GITHUB AI LOOP ENGINE

Método operativo de ejecución continua — NO-STOP / GAP-RESOLUTION / X-RAY


---

0. REGLA MAESTRA DEL SISTEMA

INPUT BLOCK
     ↓
LEER
     ↓
ANOTAR EN PIPELINE
     ↓
AUDITORÍA FORENSE X-RAY
     ↓
PLANIFICACIÓN COMPLETA POR LOTES
     ↓
EJECUCIÓN EN LOOP
     ↓
VERIFICACIÓN
     ↓
GAP
 ┌───┴───────────────────────┐
 │                           │
NO                          SÍ
 │                           │
 ↓                           ↓
CONTINUAR              INVESTIGAR 20 SOLUCIONES
                             ↓
                        DIAGNOSTICAR
                             ↓
                          RESOLVER
                             ↓
                         VERIFICAR
                             ↓
                         CONTINUAR
                             │
                             └──────────→ LOOP
                                         ↓
                              SEGUNDA PASADA
                                         ↓
                              X-RAY FORENSE
                                         ↓
                              VERIFICACIÓN CRUZADA
                                         ↓
                              INPUT BLOCK FINAL
                                         ↓
                                  100% PASS

REGLA ABSOLUTA

NO STOP.

Un GAP no termina el procesamiento.

Un error no termina el procesamiento.

Un fallo de GitHub no termina el procesamiento.

Un commit pendiente no termina el procesamiento.

Una espera de GitHub no termina el procesamiento.

Una tarea bloqueada temporalmente no bloquea las tareas independientes.

El agente debe:

> diagnosticar → resolver → verificar → continuar → volver al GAP → repetir hasta PASS.




---

1. INPUT BLOCK — CONTRATO DE ENTRADA

Antes de hacer cualquier cosa, el agente debe crear un bloque de entrada:

INPUT BLOCK

TAREA:
[texto exacto recibido]

OBJETIVO:
[resultado requerido]

FUENTE:
[repo / archivo / URL / commit]

DESTINOS:
[repositorios / archivos / ramas]

ALCANCE:
[qué puede modificar]

FUERA DE ALCANCE:
[qué NO puede modificar]

REGLAS ESPECIALES:
[restricciones]

CRITERIO PASS:
[condición exacta]

CRITERIO FINAL:
[qué significa 100% terminado]

Regla

El INPUT BLOCK es el contrato de la tarea.

No debe reinterpretarse durante el procesamiento.

Si existe ambigüedad:

INPUT BLOCK
↓
IDENTIFICAR AMBIGÜEDAD
↓
INVESTIGAR CONTEXTO DISPONIBLE
↓
PIPELINE
↓
MÉTODO DE TRABAJO
↓
DECIDIR DENTRO DEL ALCANCE

No inventar requisitos.


---

2. PRIMERA SALIDA OBLIGATORIA — X-RAY

La primera salida operativa no ejecuta cambios.

Debe hacer:

INPUT BLOCK
+
MÉTODO DE TRABAJO
+
PIPELINE
+
BITÁCORA
+
REPOSITORIO
        ↓
AUDITORÍA FORENSE X-RAY

Comprobar:

1. Método de trabajo vigente.


2. Pipeline existente.


3. Bitácora existente.


4. Estado anterior de la tarea.


5. Commits anteriores.


6. Cambios ya realizados.


7. Tareas completadas.


8. Tareas pendientes.


9. GAPs anteriores.


10. Errores anteriores.


11. Intentos anteriores.


12. Criterios de PASS.


13. Alcance.


14. Archivos autorizados.


15. Archivos protegidos.


16. Dependencias.


17. Estado de GitHub.


18. Evidencia disponible.


19. Último punto de continuidad.


20. Riesgo de duplicar trabajo.



Resultado obligatorio

X-RAY STATUS

TASK:
[ ]

PREVIOUS STATE:
[ ]

COMPLETED:
[ ]

PENDING:
[ ]

GAPS:
[ ]

LAST VERIFIED POINT:
[ ]

NEXT VALID ACTION:
[ ]

SCOPE:
[ ]

PASS CRITERIA:
[ ]


---

3. REGISTRO INMEDIATO EN PIPELINE

Antes de ejecutar, escribir/anotar la tarea en el PIPELINE.

Debe quedar:

TASK ID:
T-XXXX

TASK:
[ ]

INPUT BLOCK:
[ ]

OBJECTIVE:
[ ]

SOURCE:
[ ]

DESTINATIONS:
[ ]

SCOPE:
[ ]

PASS CRITERIA:
[ ]

X-RAY:
PASS

CURRENT STATE:
[ ]

NEXT ACTION:
[ ]

El Pipeline se convierte en memoria externa de respaldo.

Regla anti-alucinación

El agente no debe confiar solamente en su memoria conversacional.

En cada nueva tarea:

NUEVA TAREA
 ↓
LEER INPUT BLOCK
 ↓
LEER PIPELINE
 ↓
LEER BITÁCORA
 ↓
LEER MÉTODO
 ↓
X-RAY
 ↓
CONTINUAR


---

4. PASO 1 — PLANIFICACIÓN EN LOTES

No empezar ejecutando tarea por tarea sin planificación.

Primero crear el mapa completo.

Ejemplo:

LOTE 1 — INVENTARIO
LOTE 2 — AUDITORÍA
LOTE 3 — PREPARACIÓN
LOTE 4 — EJECUCIÓN
LOTE 5 — VERIFICACIÓN
LOTE 6 — SEGUNDA PASADA
LOTE 7 — X-RAY
LOTE 8 — AUDITORÍA FINAL

Si existen hasta 20 tareas:

T01
T02
T03
...
T20

Cada tarea debe tener:

ID
OBJETIVO
REPO
ARCHIVO
ACCIÓN
DEPENDENCIAS
PASS
ESTADO


---

5. PASO 2 — EJECUCIÓN TOTAL EN LOOP

Una vez terminada la planificación:

PLAN
 ↓
T01
 ↓
T02
 ↓
T03
 ↓
...
 ↓
T20

Pero no se permite salir del LOOP porque una tarea tenga GAP.

Ejemplo:

T01 → PASS
T02 → PASS
T03 → GAP
       ↓
   INVESTIGAR
       ↓
   RESOLVER
       ↓
   VERIFICAR
       ↓
   PASS
       ↓
T04

Y si T03 necesita esperar a GitHub:

T03 → WAIT
       ↓
T04 → ejecutar
T05 → ejecutar
T06 → verificar
       ↓
T03 → comprobar nuevamente
       ↓
PASS


---

6. MOTOR DE GAP — 20 VÍAS DE SOLUCIÓN

Cuando aparece un GAP, el agente no debe detenerse inmediatamente.

Debe investigar hasta 20 vías razonables de resolución, priorizadas.

GAP
 ↓
DIAGNÓSTICO
 ↓
CAUSA RAÍZ
 ↓
SOLUCIÓN 1
SOLUCIÓN 2
SOLUCIÓN 3
...
SOLUCIÓN 20
 ↓
COMPARAR
 ↓
ELEGIR SOLUCIÓN SEGURA
 ↓
EJECUTAR
 ↓
VERIFICAR

Las 20 vías no significan ejecutar cambios destructivos indiscriminadamente.

Significan investigar 20 rutas posibles, por ejemplo:

1. revisar documentación;


2. revisar API;


3. revisar permisos;


4. revisar rama;


5. revisar SHA;


6. revisar árbol;


7. revisar blob;


8. revisar commit;


9. revisar endpoint;


10. revisar estado remoto;


11. revisar historial;


12. comparar otro repositorio;


13. probar operación equivalente;


14. dividir operación;


15. cambiar estrategia de escritura;


16. reintentar operación segura;


17. comprobar eventual consistency;


18. usar mecanismo alternativo permitido;


19. verificar resultado desde otra ruta;


20. reconstruir operación desde la causa raíz.



Regla

No probar soluciones destructivas solo para “hacer que pase”.

Toda solución debe respetar:

alcance;

seguridad;

integridad;

método de trabajo;

criterio PASS.



---

7. GAP NO BLOQUEA EL RESTO

Si una tarea está esperando:

T03 = WAIT

y T04–T10 son independientes:

T03 WAIT
   ║
   ╠══ T04 RUN
   ╠══ T05 RUN
   ╠══ T06 RUN
   ╠══ T07 VERIFY
   ╚══ T08 RUN

Después:

VOLVER A T03
 ↓
RECHECK
 ↓
RESOLVE
 ↓
VERIFY


---

8. ESPERA DE GITHUB

Si una operación necesita commit, push, actualización remota o propagación:

COMMIT / PUSH
 ↓
ESPERAR 10–20 SEGUNDOS

Durante esa espera:

no quedarse inactivo si existen tareas independientes.

GITHUB WAIT
 ↓
TAREA INDEPENDIENTE
 ↓
AUDITORÍA / VERIFICACIÓN
 ↓
OTRA TAREA
 ↓
VOLVER A GITHUB
 ↓
READ-BACK

Nunca declarar PASS solamente porque GitHub aceptó el commit.

Debe hacerse:

WRITE
 ↓
WAIT
 ↓
READ-BACK
 ↓
COMPARE
 ↓
PASS


---

9. VERIFICACIÓN INMEDIATA

Cada modificación debe tener su propio ciclo:

WRITE
 ↓
COMMIT
 ↓
PUSH
 ↓
WAIT
 ↓
READ
 ↓
COMPARE
 ↓
PASS

Si falla:

FAIL
 ↓
GAP ENGINE
 ↓
RESOLVE
 ↓
RETRY
 ↓
VERIFY


---

10. PIPELINE COMO MEMORIA EXTERNA

Después de cada cambio importante:

actualizar el Pipeline.

Registrar:

TASK ID
TIME
REPO
FILE
ACTION
OLD STATE
NEW STATE
COMMIT
SHA
VERIFICATION
GAP
SOLUTION
NEXT ACTION

Ejemplo:

T07
Repo: X
File: Y
Action: UPDATE
Commit: abc123
Read-back: PASS
Content verification: PASS
Next: T08

Esto evita que el agente tenga que reconstruir el estado desde memoria interna.


---

11. BITÁCORA

La bitácora registra el historial completo:

FECHA
TAREA
ACCIÓN
RESULTADO
GAP
DIAGNÓSTICO
SOLUCIÓN
COMMIT
VERIFICACIÓN
SIGUIENTE PASO

Regla

Pipeline = estado actual.

Bitácora = historial.

Input Block = contrato original.

Método de trabajo = reglas del sistema.


---

12. RELECTURA OBLIGATORIA EN CADA NUEVA TAREA

Antes de comenzar T02:

LEER INPUT BLOCK
 ↓
LEER PIPELINE
 ↓
LEER BITÁCORA
 ↓
COMPROBAR T01
 ↓
X-RAY
 ↓
T02

Antes de T03:

LEER INPUT BLOCK
 ↓
LEER PIPELINE
 ↓
LEER BITÁCORA
 ↓
COMPROBAR T02
 ↓
X-RAY
 ↓
T03

Y así sucesivamente.

Esto evita:

perder el objetivo;

duplicar trabajo;

olvidar un GAP;

mezclar tareas;

inventar estados.



---

13. CONTROL DE ENFOQUE

En cada transición:

¿ESTOY HACIENDO PARTE DEL INPUT BLOCK?
          ↓
       SÍ → CONTINUAR
          ↓
       NO → NO EJECUTAR

Si aparece una tarea nueva:

TAREA NUEVA
 ↓
NO MEZCLAR
 ↓
REGISTRAR COMO NUEVA TAREA
 ↓
CONTINUAR TAREA ACTUAL


---

14. SEGUNDA PASADA OBLIGATORIA

Nunca declarar terminado después de la primera pasada.

PRIMERA PASADA
 ↓
TODAS LAS TAREAS
 ↓
SEGUNDA PASADA
 ↓
TODAS LAS TAREAS NUEVAMENTE

Buscar:

archivos faltantes;

cambios incompletos;

commits incorrectos;

SHA incorrectos;

contenido diferente;

tareas olvidadas;

GAPs ocultos.



---

15. FORENSE X-RAY FINAL

Comprobar simultáneamente:

INPUT BLOCK
     ↕
PIPELINE
     ↕
BITÁCORA
     ↕
GITHUB
     ↕
COMMITS
     ↕
ARCHIVOS
     ↕
SHA

Debe existir coherencia completa.


---

16. VERIFICACIÓN CRUZADA FINAL

La última auditoría debe responder:

INPUT BLOCK

¿Se cumplió exactamente?

PIPELINE

¿Todos los estados están registrados?

BITÁCORA

¿Todos los cambios están documentados?

GITHUB

¿Los cambios realmente existen?

COMMITS

¿Cada cambio tiene evidencia?

ENLACES

¿Cada cambio puede abrirse y comprobarse?

ALCANCE

¿No se modificó nada ajeno?

TAREAS

¿Las 20 tareas, si existen, están en PASS?


---

17. ENLACE OBLIGATORIO POR CAMBIO

Para cada modificación GitHub:

REPO:
[ ]

ARCHIVO:
[ ]

COMMIT:
[ ]

ENLACE:
[ ]

VERIFICACIÓN:
PASS

El enlace debe permitir comprobar directamente el cambio.

No decir:

> “Está hecho.”



Debe existir evidencia navegable.


---

18. ESTADO DE CADA TAREA

Estados permitidos:

QUEUED
RUNNING
WAITING
GAP
RESEARCHING
RESOLVING
VERIFYING
PASS

DONE solamente después de PASS.


---

19. CONDICIÓN DE NO-STOP

El agente no puede abandonar el LOOP simplemente porque:

apareció un GAP;

GitHub respondió con error;

una API tardó;

un commit está propagándose;

una operación falló;

una tarea necesita otra estrategia;

un repositorio está temporalmente inaccesible;

una primera solución no funcionó.


Debe:

ERROR
 ↓
DIAGNÓSTICO
 ↓
20 VÍAS DE INVESTIGACIÓN
 ↓
SOLUCIÓN
 ↓
VERIFICACIÓN
 ↓
CONTINUAR

Excepción real

Si existe una imposibilidad externa auténtica que no puede resolverse mediante las herramientas disponibles, no inventar PASS.

Registrar:

EXTERNAL BLOCK
EVIDENCE
ATTEMPTS
20-WAY ANALYSIS
CURRENT STATE
NEXT RECOVERY POINT

y conservar todo en Pipeline/Bitácora.

Pero no convertir un error ordinario en “bloqueo externo” para escapar del LOOP.


---

20. CIERRE DEL CICLO

Solo cerrar cuando:

T01 PASS
T02 PASS
T03 PASS
...
T20 PASS
       ↓
SEGUNDA PASADA PASS
       ↓
X-RAY PASS
       ↓
INPUT BLOCK PASS
       ↓
PIPELINE PASS
       ↓
BITÁCORA PASS
       ↓
GITHUB PASS
       ↓
ENLACES VERIFICADOS
       ↓
SIN GAPS
       ↓
SIN PENDIENTES
       ↓
100% PASS

LOOP MAESTRO FINAL

┌───────────────────────────────────────────────┐
│                 INPUT BLOCK                   │
└──────────────────────┬────────────────────────┘
                       ↓
              LEER MÉTODO DE TRABAJO
                       ↓
                 LEER PIPELINE
                       ↓
                 LEER BITÁCORA
                       ↓
                FORENSE X-RAY
                       ↓
             PLANIFICAR POR LOTES
                       ↓
             ┌─────────────────┐
             │   LOOP TAREAS   │
             └────────┬────────┘
                      ↓
                EJECUTAR TAREA
                      ↓
                   VERIFY
                      ↓
               ┌──────┴──────┐
               │             │
             PASS           GAP
               │             │
               │             ↓
               │       DIAGNOSTICAR
               │             ↓
               │      INVESTIGAR ×20
               │             ↓
               │         RESOLVER
               │             ↓
               │         VERIFICAR
               │             │
               │             └──────→ LOOP
               ↓
          REGISTRAR PIPELINE
               ↓
          REGISTRAR BITÁCORA
               ↓
          SIGUIENTE TAREA
               ↓
          LEER INPUT BLOCK
               ↓
          LEER PIPELINE
               ↓
          REVISAR ENFOQUE
               ↓
          CONTINUAR LOOP
               ↓
        SEGUNDA PASADA COMPLETA
               ↓
         FORENSE X-RAY FINAL
               ↓
       VERIFICACIÓN CRUZADA FINAL
               ↓
      INPUT BLOCK ↔ PIPELINE ↔ GITHUB
               ↓
       ENLACES DE CADA CAMBIO
               ↓
            100% PASS
               ↓
          CERRAR TAREA

PRINCIPIO FUNDAMENTAL

> El agente no trabaja para producir una respuesta; trabaja para llevar el estado real de GitHub desde el estado inicial del INPUT BLOCK hasta el estado final verificable de 100% PASS.



Y:

> La memoria de trabajo no puede depender de lo que el agente “recuerde”: debe quedar reconstruible desde INPUT BLOCK + PIPELINE + BITÁCORA + GitHub.



Esta versión ya incorpora planificación en lote + ejecución continua + hasta 20 tareas + GAP engine + investigación de 20 soluciones + espera activa + paralelización de tareas independientes + doble pasada + X-Ray + memoria persistente + enlaces de evidencia + verificación cruzada final.


# PIPELINE 00 — MÉTODO DE TRABAJO + ARQUITECTURA

**Repo hermano:** maxbry-router · Fuente canónica también en `maxbry123-commits/agentes`  
**Arquitectura REAL programación:** `PIPELINE/ARQUITECTURA_WORDFLOW_PROGRAMMING.md`  
**Mapa forense:** `PIPELINE/WORDFLOW_PROGRAMMING_FORENSIC_MAP.md`  
**Forense checklist:** `PIPELINE/FORENSIC_CODE_AUDIT.md`  
**Gaps:** `PIPELINE/GAPS_PROGRAMMING_WORDFLOW.md`  
**Pipeline code:** `extensions/wordflow/engine/programming_pipeline.py`  
**Hot path:** `extensions/wordflow/engine/code_path_runner.py`

## Cadena obligatoria (política)
CONTEXT/HANDOFF → COPY-FIRST SCAN → IMPLEMENT(COPY|ADAPT|GENERATE) → WIRE → FORENSIC VERIFY → VERDICT AUTHORITY → CLOSED | FIX LOOP

## Cadena REAL en code_path (arquitectura)
pre_gate → quality_bar → goal_lock → cognitive_loop → evidence → post_verify(VerdictAuthority)

## COPY-FIRST
name + catalog + AST → COPY/ADAPT; GENERATE last. Evidence SOURCE→DEST+SHA si copy_file_deterministic.

## CONTROL DE TRABAJO
1 TOTAL · 2 TERMINADAS · 3 PENDIENTES · 4 SIGUIENTE · 5 PLAN · 6 MÉTODO · 7 NO sandbox / GitHub=verdad

---

# APPEND V3 — PROTOCOLO OPERATIVO SANDBOX → GITHUB → FORENSE
**Origen:** METHOD_WORK_UPDATE_V3_SANDBOX_GITHUB_FORENSIC  
**Tipo:** APPEND_ONLY · NO sustituye reglas anteriores · COPY-FIRST · deterministic-first · VERDICT AUTHORITY · CONTROL DE TRABAJO · GitHub=verdad · STAGNATION BREAKER · trazabilidad se CONSERVAN

## Autoridad
- Método de trabajo = reglas operativas
- GitHub = fuente persistente de verdad
- Sandbox = workspace temporal (build/test/verify) · NO memoria persistente · NO = DONE
- Usuario = aprueba cierre
- Auditoría forense = veredicto técnico con evidencia (no afirmación LLM)

## Modelo operativo (no saltar a DONE)
TASK_INTAKE → SALIDA_1_SANDBOX_BUILD → LOCAL_VERIFY → READY_FOR_PUBLISH → SALIDA_2_GITHUB_PUBLISH → REMOTE_VERIFY → PUBLISHED_AND_VERIFIED → SALIDA_3_FORENSIC_AUDIT → DONE

## TASK_INTAKE (antes de ejecutar)
Leer: README · Método · PIPELINE · tarea + trazabilidad · chat si hace falta.  
Definir: TASK_ID · OBJECTIVE · SOURCES · INPUTS · OUTPUTS · DEPENDENCIES · ACCEPTANCE · TRACEABILITY · STATUS=READY

## SALIDA 1 — SANDBOX_BUILD
- Construir en Sandbox primero; no publicar aún.
- Preferir cp/cat/sed/awk/git; no transportar bytes grandes por LLM; no regenerar fuente existente.
- Registrar comandos reales.
- Manifest obligatorio: `task_build/ARTIFACT_MANIFEST.json` (task_id, path, sources, size, lines, sha256, anchors, tests, diff_status, build_status).
- Éxito: READY_FOR_PUBLISH · Nunca: DONE desde build.

## LOCAL_VERIFY
test -f · wc -c/-l · sha256sum · grep anchors · (code: git diff --check + tests).  
Gate: LOCAL_VERIFY_PASS. Sin PASS → no publicar.

## PUBLISH_GATE
Solo si LOCAL_VERIFY_PASS. Publicar el artefacto del manifest; sin regenerar/resumir/reescribir desde LLM.

## SALIDA 2 — GITHUB_PUBLISH
Persistir exactamente el artefacto verificado. Registrar repo/path/branch/commit. HTTP 200 ≠ prueba suficiente → READ-BACK obligatorio.

## REMOTE_VERIFY
Releer GitHub: size, lines, anchors, content, commit; comparar con local (sha256 si aplica).  
Fallo: PERSISTENCE_FAILURE → REPAIR · no DONE · no cleanup · no siguiente tarea.  
Éxito: PUBLISHED_AND_VERIFIED.

## SALIDA 3 — FORENSIC_AUDIT (tras cada tarea con code / cierre)
Dominios: METHOD · REQUIREMENTS · TRACEABILITY · SANDBOX_BUILD · LOCAL_VERIFY · PUBLISH · REMOTE · INTEGRITY · NO_UNAUTHORIZED · TESTS · DOCS.  
Veredictos: DONE | REPAIR_REQUIRED | BLOCKED.  
**Tras cada tarea de code:** auditoría forense de programación según FORENSIC_CODE_AUDIT + esta sección (CLAIM ≠ EVIDENCE).  
Afirmación LLM ≠ evidencia.

## TASK_COMPLETION_GATE
DONE solo si: INTAKE + LOCAL_VERIFY + GITHUB_PUBLISHED + REMOTE_VERIFY + FORENSIC_AUDIT_DONE.

## Trazabilidad post-DONE
Persistir en GitHub `TASK_COMPLETION_RECORD` (task_id, objective, sources, outputs, paths, commit, local/remote sha, verdict, next_task).

## Arquitectura en avance
Al avanzar y tocar archivos: actualizar arquitectura/trazabilidad según impacto; no regenerar fuentes; append/doc de lo tocado con evidencia.

## Recuperación de contexto
Orden: README → MÉTODO → PIPELINE → LISTA TAREAS → COMPLETION RECORDS → TRACE → DOCS REQUERIDOS → chat audit si hace falta.  
No depender solo del Sandbox ni solo de memoria de chat.

## Siguiente tarea
Solo con CURRENT_TASK=DONE y autorización usuario. No auto-iniciar.

## CLEANUP
Solo tras FORENSIC_DONE + aprobación usuario. Proteger: método, GitHub, fuentes, trazabilidad, completion records.

## STAGNATION (refuerzo)
Mismo fallo ×2 → cambiar mecanismo. Fallo publish → no regenerar documento completo. Fallo verify → reparar, no declarar éxito.



# PARCHE 01 — COMPLEMENTO FORENSE DE GUIA-DESPLIEGUE-ZIP-UNIVERSAL

**Estado:** ACTIVO  
**Regla:** complemento aditivo; NO reemplaza ni borra `GUIA-DESPLIEGUE-ZIP-UNIVERSAL.md`.

## 1. Gaps detectados en la auditoría X-Ray

La guía principal cubre extracción, staging, hashes, estructura, cuatro pasadas, lotes, duplicados, raíces protegidas y read-back. Esta revisión añade controles que conviene ejecutar antes de aceptar cualquier ZIP de software:

- **ZIP bomb / expansión excesiva:** registrar tamaño comprimido y tamaño estimado/descomprimido; establecer un límite operativo antes de extraer.
- **Entradas especiales:** revisar symlinks, hardlinks, dispositivos, FIFOs y permisos antes de publicar. No ejecutar ni convertir automáticamente una entrada especial en archivo normal.
- **Path traversal robusto:** rechazar rutas absolutas y cualquier ruta normalizada que escape del staging.
- **Archivos ocultos y configuración:** inventariar `.env*`, `.git*`, claves, certificados y archivos de configuración; nunca publicar secretos por accidente.
- **Credenciales:** buscar patrones de tokens/llaves y detenerse para revisión si aparecen credenciales. No imprimir valores secretos en logs.
- **Licencias y notices:** identificar `LICENSE`, `NOTICE`, `COPYING` y avisos de terceros y conservarlos cuando formen parte de la distribución.
- **Git LFS / punteros:** detectar archivos que sean punteros LFS y comprobar que el contenido real requerido esté disponible antes de declarar PASS.
- **Archivos grandes:** identificar tamaños anómalos antes del commit y comprobar límites de GitHub/estrategia de almacenamiento.
- **Permisos ejecutables:** registrar cambios de modo/permisos cuando sean relevantes; no otorgar ejecutabilidad por defecto.
- **Enlaces simbólicos:** conservarlos solo cuando sean seguros y soportados; verificar que no apunten fuera de la raíz publicada.
- **Reproducibilidad:** registrar nombre, versión/ref, origen, SHA del ZIP, commit upstream cuando exista y manifest final.
- **Dependencias:** la extracción no implica instalación. Instalar/ejecutar dependencias es una fase posterior y explícita.
- **Build/test:** no declarar que el software funciona solo porque los archivos fueron extraídos; separar `DEPLOY_PASS` de `RUNTIME_TEST_PASS`.
- **Rollback:** conservar commit base y manifest previo para poder restaurar una raíz si la publicación posterior falla.
- **Cambio de destino:** nunca reutilizar una raíz existente sin comparar el árbol previo con el árbol candidato.

## 2. Controles adicionales del DAG

Añadir conceptualmente estos nodos al DAG principal:

```text
ZIP_RECEIVED
  -> SIZE_GUARD
  -> ZIP_BOMB_GUARD
  -> ENTRY_TYPE_GUARD
  -> SECRET_SCAN
  -> LICENSE_NOTICE_SCAN
  -> LFS_POINTER_SCAN
  -> LARGE_FILE_SCAN
  -> PERMISSION_SCAN
  -> STAGING
```

Y antes de `COMMIT`:

```text
PRE_COMMIT_SECURITY_AUDIT
  -> DESTINATION_DIFF
  -> ROLLBACK_POINT
  -> COMMIT
```

## 3. Comandos de referencia adicionales

No se deben marcar como ejecutados salvo que exista evidencia del runner.

```bash
# tamaño comprimido
stat -c '%s' software.zip

# tamaños y tipos de entradas
unzip -l software.zip
unzip -Z1 software.zip

# detectar punteros Git LFS después de extracción
find .staging/software -type f -print0 | xargs -0 grep -Il '^version https://git-lfs.github.com/spec/v1$' || true

# detectar archivos grandes en staging (ejemplo: >100 MiB)
find .staging/software -type f -size +100M -print

# revisar symlinks
find .staging/software -type l -ls

# revisar rutas reales de symlinks
find .staging/software -type l -exec readlink -f {} \;

# inventario de licencias/notices
find .staging/software -type f \( -iname 'LICENSE*' -o -iname 'NOTICE*' -o -iname 'COPYING*' \) -print

# detectar archivos potencialmente sensibles por nombre; revisar manualmente
find .staging/software -type f \( -iname '.env' -o -iname '.env.*' -o -iname '*secret*' -o -iname '*credential*' -o -iname '*.pem' -o -iname '*.key' \) -print
```

## 4. Regla de secretos

El pipeline **no debe copiar secretos del ZIP a GitHub**. Si el software legítimamente necesita credenciales, se debe convertir esa necesidad en configuración por entorno/Secret y registrar solamente la referencia, nunca el valor.

```text
ZIP
 -> SECRET_SCAN
 -> si detecta secreto: BLOCKED
 -> revisión humana
 -> retirar/aislar el secreto
 -> volver a verificar
 -> PASS
```

## 5. Regla ZIP bomb

No existe un único límite universal para todos los softwares. El pipeline debe definir un límite operativo por tarea y detener la extracción si el tamaño esperado supera ese límite.

```text
compressed_size
uncompressed_size
file_count
compression_ratio
       ↓
SIZE_GUARD
       ↓
ALLOW / BLOCKED
```

Nunca extraer un ZIP sospechoso directamente sobre `ROOTS/`.

## 6. Regla de seguridad de rutas

Antes de publicar cada entrada:

```text
archive path
  ↓ normalize
  ↓ reject absolute
  ↓ reject ../ escape
  ↓ resolve inside staging
  ↓ map relative path
  ↓ publish
```

Una ruta que no pueda demostrar que permanece dentro del staging se clasifica `BLOCKED`.

## 7. Separación de estados

La guía principal debe interpretarse con estos estados independientes:

```text
EXTRACTION_PASS
DEPLOY_PASS
UPSTREAM_CROSSCHECK_PASS
SECURITY_PASS
RUNTIME_TEST_PASS
```

Un software puede tener `DEPLOY_PASS` y todavía no tener `RUNTIME_TEST_PASS`.

## 8. Rollback

Antes de modificar una raíz existente:

```text
BASE_COMMIT
BASE_MANIFEST
BASE_SHA
      ↓
CANDIDATE
      ↓
AUDIT
      ↓
COMMIT
```

Si la verificación post-publicación falla, restaurar mediante un commit/revert controlado; no borrar a ciegas la raíz.

## 9. Auditoría X-Ray de este parche

### Pasada 1 — contra la guía principal

Confirmado que este archivo solo añade controles y no sustituye instrucciones existentes.

### Pasada 2 — contra la bitácora/PIPELINE

Los controles mantienen las reglas existentes: staging primero, hashes, cuatro pasadas, protección de raíces, evidencia antes de `DONE`.

### Pasada 3 — contra el método de despliegue del Wordflow Core

Se conserva la separación entre preparación de archivos y publicación determinista. La extracción no se convierte en ejecución del software.

### Pasada 4 — consistencia operacional

El parche añade seguridad, rollback, secretos, LFS, archivos grandes, entradas especiales, licencias, permisos y separación de pruebas sin cambiar la arquitectura `ROOTS/<software>/`.

## 10. Cómo se aplica

Este parche se consulta junto con la guía principal:

```text
GUIA-DESPLIEGUE-ZIP-UNIVERSAL.md
                +
GUIA-DESPLIEGUE-ZIP-UNIVERSAL-PARCCHE-01.md
                ↓
          método completo
```

**No editar ni reemplazar la guía principal para incorporar este parche.** Si en el futuro aparece otro gap, crear `PARCHE-02` y registrar la relación en la bitácora.
