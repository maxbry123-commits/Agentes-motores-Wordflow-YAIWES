# INPUT BLOCK — plantilla de plan (leer literal)

## 1. Destino y extracción
- Repo destino: `Agentes-motores-Wordflow-YAIWES`, rama `main`.
- Cada elemento tendrá una única raíz propia.
- La raíz usará el nombre exacto del repositorio/agente indicado en el inventario.
- Dentro de esa raíz estará el contenido completo extraído del ZIP.
- Nada de archivos/repositorios sueltos fuera de la raíz correspondiente.
- No se mezclan contenidos entre repos.

## 2. Lista
- La fuente de verdad será exactamente el inventario del plan vigente.
- Se procesan todos los elementos de la lista, incluidos los que aparecen al final.
- No se aplican filtros por popularidad, categoría, antigüedad o utilidad.
- No se eliminan elementos de la lista por decisión propia.
- No se asigna URL inventada.

## 3. GitHub Action
- La acción tiene como objetivo exclusivamente los elementos del inventario.
- No se reutiliza accidentalmente la acción anterior como si fuera la nueva descarga.
- No se añaden repositorios que no estén en la lista.

## 4. Código
- Solo el código/skills y el procedimiento de referencia.
- El código mostrado como ejemplo no se trata como otro repositorio para descargar.
- No se inventa un downloader, extractor, arquitectura ni tercer proceso.
- La implementación respeta el código de referencia del skill.

## 5. Los únicos 2 pasos del Wordflow
PASO 1 Descargar en ZIP todos los repos de la lista
PASO 2 Extraer cada ZIP en su propia raíz con el nombre exacto correspondiente

Plan de ejecución: `INVENTARIO → DOWNLOAD ZIP → EXTRACT → raíz individual por repo → main`
