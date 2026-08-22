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
