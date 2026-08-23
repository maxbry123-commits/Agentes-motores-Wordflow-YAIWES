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

