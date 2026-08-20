# ACR Recovery Patch — OpenClaw Motor

Este archivo es el mapa visible de recuperación del proceso ACR para descargar OpenClaw como motor de Wordflow, sin la UI.

## Regla de trabajo
1. Auditar la raíz y manifests antes de descargar.
2. Fijar commit/SHA de cada archivo fuente.
3. Para archivos grandes, recuperar por segmentos cuando el canal limite la transferencia.
4. Nunca contar un parcial como descargado.
5. Reconstruir y verificar contra el SHA/blob fuente antes de cerrar un archivo.
6. Si una escritura falla, obtener el SHA real del destino antes de eliminar/reintentar.
7. Registrar cada incidencia, solución, última salida y siguiente salida para permitir recuperación por otro GPT/agente.

## Incidencias documentadas
- **Blob truncado:** una lectura de archivo grande puede devolver contenido incompleto. **Solución:** recuperar el blob completo y usar segmentación/reconstrucción, sin inventar contenido.
- **SHA equivocado:** una búsqueda puede devolver un archivo de otro commit. **Solución:** mantener el commit fuente fijado y descartar resultados de otros commits.
- **Escritura parcial:** una prueba de escritura creó un fragmento de `openclaw.mjs`. **Solución:** recuperar el SHA real del archivo parcial, eliminarlo y reiniciar desde cero.
- **Escritura bloqueada:** el conector rechazó una operación que no podía garantizar integridad. **Solución:** no forzarla; conservar el destino limpio y cambiar a transferencia exacta del blob.

## Estado actual
- Fuente: `openclaw/openclaw`
- Destino: `maxbry123-commits/Agentes-motores-Wordflow-YAIWES`
- Branch ACR: `acr/openclaw-motor-recovery-v2`
- Archivo actual: `openclaw.mjs`
- SHA fuente: `d624faf3604c29b01cacefec011e753c5679daea`
- Transferencia válida al destino: pendiente
- UI: excluida del alcance

## Continuación
Última salida: 46
Siguiente salida: completar la actualización de la bitácora y continuar la transferencia exacta de `openclaw.mjs`.
