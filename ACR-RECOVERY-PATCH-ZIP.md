# ACR Recovery Patch — ZIP OpenClaw

## 1. Fuente única
- Repositorio fuente: `openclaw/openclaw`
- Ref exacto: `a4178c7eb15a0dd2b8b44804348e256f1a109a34`
- El ZIP de este ref es la única fuente de archivos OpenClaw para este despliegue.
- No comparar contra `ACR/source/root` para decidir qué copiar.
- No borrar ni modificar `ACR/`, la bitácora ni este parche durante la operación.

## 2. Descarga oficial del ZIP
GitHub documenta `GET /repos/{owner}/{repo}/zipball/{ref}` para descargar un ZIP del repositorio. El endpoint responde `302 Found`; el cliente debe seguir `Location`. Para un repositorio público no se requiere autenticación. Se puede usar `curl -L`, JavaScript o GitHub CLI.

Ejemplo:
`curl -L -H "Accept: application/vnd.github+json" https://api.github.com/repos/openclaw/openclaw/zipball/a4178c7eb15a0dd2b8b44804348e256f1a109a34 -o openclaw-a4178c7.zip`

### Solución de transferencia cuando el conector no puede guardar el ZIP
- No sustituir el ref exacto por `main`, un tag o una release.
- Ejecutar la descarga en un entorno con capacidad de seguir HTTP `302` y guardar bytes binarios (`curl -L`, GitHub CLI o un cliente HTTP equivalente).
- Después de guardar el ZIP, calcular su hash y tamaño antes de extraerlo.
- El archivo descargado debe quedar disponible para el paso de extracción; no declarar la descarga completada si no existe el ZIP real.
- Los ZIP de Source code de una release sólo pueden usarse si se verifica que corresponden exactamente al ref SHA requerido; de lo contrario no son sustitutos.

## 3. Preparación del destino
- Eliminar únicamente los archivos OpenClaw creados previamente por este proceso.
- Eliminar el Ledger creado previamente si corresponde a esos artefactos.
- Conservar `ACR/`, la bitácora y el parche.
- No borrar ni alterar evidencia ACR histórica.

## 4. Extracción y despliegue
- Extraer el ZIP.
- Desplegar su contenido en la raíz del repositorio de recuperación.
- Mantener exactamente las rutas relativas.
- Mantener symlinks como symlinks.

## 5. Verificación
- Verificar que el ZIP se descargó completo.
- Inventariar archivos, tamaños, SHA y `mode`.
- Comparar la raíz desplegada exclusivamente contra el inventario del ZIP.
- Confirmar que no falta ningún archivo y que los symlinks conservan su modo.

## 6. Límites GitHub relevantes
- GitHub aplica un máximo de 100 MiB por objeto Git individual.
- El límite de push es 2 GiB.
- Para contenidos de 1–100 MB, Contents API requiere media type `raw` u `object`; por encima de 100 MB ese endpoint no está soportado.
- El ZIP completo no se trata como un único objeto Git durante el despliegue: se extraen sus archivos y se escriben como objetos Git individuales.

## 7. Registro
- Registrar en Ledger y bitácora la descarga, ref, tamaño, inventario, SHA, commit y resultado de verificación.
- Una operación sólo se considera completada cuando GitHub devuelve evidencia verificable del commit y una lectura posterior confirma el contenido.

## 8. Estado
ZIP = única fuente de archivos OpenClaw.
ACR = evidencia/instrumentación, no fuente alternativa de copia.

## 9. Incidencia de transferencia investigada
- El conector GitHub disponible en esta sesión no puede seguir/guardar directamente el binario devuelto por el `zipball` (`302` → `Location`).
- La solución integral es realizar la transferencia en un entorno con descarga HTTP binaria y seguimiento de redirecciones, conservar el ZIP real, verificar hash/tamaño y continuar inmediatamente con extracción y despliegue.
- Esta limitación del entorno no debe registrarse como una descarga exitosa.
