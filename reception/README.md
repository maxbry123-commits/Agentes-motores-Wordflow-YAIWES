# Sistema de subida de documentos — maxbry-router

## Cómo subir
1. Abre este repo en GitHub.
2. Ve a la carpeta `reception/` (o crea archivo en ella).
3. **Add file → Upload files** (o Create new file).
4. Sube `.md` / `.yaml` / `.json` / `.txt` del trabajo.
5. Commit a `main` (o abre PR).

## Cómo funciona
- `reception/` = bandeja de entrada del repo.
- El agente/Wordflow lee **literal** los archivos aquí (FC-08 Context).
- Sin documento en reception + handoff verificado → **NO programar** (regla obligatoria).
- Trazabilidad: cada doc debe declarar misión/tarea/origen en el schema abajo.

## Enlaces
- Método: https://github.com/maxbry123-commits/agentes/blob/main/PIPELINE/00_METODO_TRABAJO_Y_ARQUITECTURA.md
- Forense: https://github.com/maxbry123-commits/agentes/blob/main/PIPELINE/FORENSIC_CODE_AUDIT.md
- Handoff: https://github.com/maxbry123-commits/agentes/blob/main/README_FORENSIC_HANDOFF.md
