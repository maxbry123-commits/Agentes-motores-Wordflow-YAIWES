# Plantilla de plan — Download ZIP → Extract raíz

Usar esta plantilla en todos los planes. No incrustar aquí el inventario numerado.

## Destino y extracción
- Repo destino y rama: los que fije el plan vigente.
- Cada elemento tiene una única raíz propia.
- La raíz usa el nombre exacto del ítem en el inventario del plan.
- Dentro de esa raíz va el contenido completo extraído del ZIP.
- Nada suelto fuera de su raíz. No mezclar contenidos entre repos.

## Lista
- Fuente de verdad: el inventario del plan vigente.
- Se procesan todos los elementos, incluidos los del final.
- Sin filtros por popularidad, categoría, antigüedad o utilidad.
- No se elimina ningún elemento por decisión propia.
- Si un ítem no tiene URL fijada, queda en la lista y no se inventa URL.

## GitHub Action
- La acción apunta solo al inventario de ese plan.
- No se reutiliza una acción anterior como si fuera la nueva descarga.
- No se añaden repositorios que no estén en la lista.

## Código
- Solo el procedimiento de referencia de este skill.
- El código de ejemplo no se trata como otro repositorio a descargar.
- No se inventa downloader, extractor, arquitectura ni tercer proceso.

## Únicos 2 pasos
1. Descargar en ZIP los repos del inventario que tengan URL fijada.
2. Extraer cada ZIP en su propia raíz con el nombre exacto correspondiente.

Cadena: `INVENTARIO → DOWNLOAD ZIP → EXTRACT → raíz individual → main`
