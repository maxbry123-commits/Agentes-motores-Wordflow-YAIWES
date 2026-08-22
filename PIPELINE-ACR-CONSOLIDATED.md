# PIPELINE ACR — CONSOLIDADO PARA FUTUROS AGENTES

## 1. Objetivo
Este documento es el mapa operativo para GPT, Grok u otro agente que continúe el repositorio. Contiene el método, los gaps conocidos, las soluciones aplicadas, la reconstrucción de OpenClaw desde ZIPs, la verificación cruzada y el laboratorio CPU reutilizable.

## 2. Arquitectura
```text
repo/
├── ROOTS/
│   ├── openclaw/          # raíz exclusiva de OpenClaw
│   └── <otros-agentes>/   # futuras raíces hermanas
├── .github/workflows/     # pipeline/control, fuera de las raíces
├── FORENSIC-ZIP/          # evidencia de ZIPs
├── BITACORA-ACR-XRAY.md   # memoria operativa persistente
├── OPENCLAW-ROOT-MANIFEST.md
└── FORENSIC-CROSSCHECK-OPENCLAW.md
```

## 3. Método de trabajo
`TASK_INTAKE → INVENTORY → ZIP_XRAY → CANONICAL_COMPARE → BUILD_SANDBOX → LOCAL_VERIFY → PUBLISH → REMOTE_READBACK → FORENSIC_XRAY → DONE`.

Reglas: GitHub es la fuente persistente de verdad; un plan no es una ejecución; un HTTP 200 no demuestra canonicidad; cada publicación requiere read-back; los hashes son evidencia; si el mismo mecanismo falla dos veces se cambia el mecanismo; nunca marcar DONE sin evidencia.

## 4. Reconstrucción por lotes ZIP
Se identificaron 8 ZIPs y 14698 rutas relativas únicas en su unión. ZIP1 y ZIP4 son duplicados exactos (1355 rutas/hashes). ZIP5, ZIP5.1, ZIP6, ZIP7, ZIP8 y ZIP9 aportan conjuntos complementarios.

Flujo usado:
1. Recuperar ZIP mediante GitHub Actions/artifact cuando el blob grande no podía leerse directamente.
2. `unzip -t` para validar integridad.
3. Extraer preservando rutas relativas.
4. Generar inventario y SHA-256 por archivo.
5. Comparar ZIP↔ZIP para duplicados y overlaps.
6. Quitar solo la envoltura técnica `extracted/`.
7. Comparar ZIP↔OpenClaw oficial por ruta y contenido.
8. Construir `ROOTS/openclaw/` usando el ref canónico como autoridad y los ZIP como evidencia cruzada.
9. Excluir dependencias/artefactos generados (`node_modules`, `.pnpm-store`, `dist`, `build`, `coverage`, `.cache`, `.tmp`, logs).
10. Generar manifest de ruta, SHA-256, tamaño y modo.
11. Publicar en GitHub.
12. Hacer read-back y repetir XRAY.

Distribución observada: ZIP1/4 `apps/config/deploy`; ZIP5 `extensions/packages/qa/patches/git-hooks`; ZIP5.1 `docs/examples`; ZIP6 `docs/config/examples/deploy`; ZIP7 `scripts/skills/security`; ZIP8 `test/ui`; ZIP9 `agents/auto-reply/acp/audit/bindings`.

## 5. Gaps detectados y tratamiento
- `package.json`: MODIFIED; comparar/corregir desde canonical.
- `node-version.mjs`: MISSING inicialmente; canonical blob `dc7876dd0ce35116aaef535d342647ebb1ad16e7`.
- `npm-shrinkwrap.json`: EXTRA/NON-CANONICAL; no confundirlo con el lockfile oficial.
- `pnpm-workspace.yaml`: MODIFIED.
- `README.md`: MODIFIED.
- `LICENSE`: MATCH.
- `THIRD_PARTY_NOTICES.md`: MATCH.
- `openclaw.mjs`: MODIFIED; canonical usa `node-version.mjs` y Node 26.
- `pnpm-lock.yaml`: inicialmente MODIFIED/incorrectamente ubicado; solucionado en `ROOTS/openclaw/` con SHA canónico `cefd1fdf77f5c170ffacfad4b75e03c4c33345cf`.
- `Dockerfile`, `tsconfig.json`, `vitest.config.ts`, `AGENTS.md`: identificados como MODIFIED y sujetos a la reconstrucción canónica.

## 6. Lockfile: procedimiento concreto
Se detectó `pnpm-lock.yaml.txt` y ZIP temporal en la raíz. Se verificó el contenido contra el SHA canónico. Se pasó a `ROOTS/openclaw/pnpm-lock.yaml` y se eliminaron los duplicados temporales. El lockfile global con SHA diferente se conservó porque no era demostrablemente el mismo blob.

## 7. Pipeline CPU reutilizable
Workflow: `.github/workflows/cpu-benchmark.yml`.

Diseño final: UNA ejecución, UNA cadena, UN artifact. Pruebas:
1. `lscpu`
2. `sysbench cpu`
3. `openssl speed sha256`
4. `7z b -mmt=4`
5. Integer/C benchmark
6. Floating point Python
7. `stress-ng`
8. SHA-256 de archivo de 256 MiB
9. JSON serialize/parse
10. scaling de 1/2/4 workers

La salida se guarda en `benchmark-results/benchmark.log` y se publica como artifact `cpu-benchmark-results`. `set -euo pipefail` impide continuar silenciosamente tras un error.

### Importante
El workflow está preparado; **la ejecución física solo se considera PASS cuando existe un run/job real y se inspeccionan logs/artifact**. No convertir la existencia del YAML en resultado de benchmark.

## 8. Commits de referencia
- `589a062...` — laboratorio CPU inicial.
- `e99539c...` — workflow CPU.
- `8296133...` — versión de 3 pasadas, luego simplificada.
- `a20565f...` — una sola batería de 10 pruebas.
- `1a52cab...` — lockfile canónico/limpieza.
- `fcb7c22...` — esta consolidación de bitácora.

## 9. Auditoría final obligatoria
```text
[ ] árbol ROOTS verificado
[ ] OpenClaw canonical ref confirmado
[ ] todos los ZIP validados
[ ] overlaps revisados
[ ] ZIP↔canonical comparado
[ ] archivos críticos comparados por SHA
[ ] exclusiones verificadas
[ ] manifest completo
[ ] publish confirmado
[ ] remote read-back
[ ] build/boot test
[ ] CPU benchmark run real
[ ] artifact CPU inspeccionado
[ ] XRAY final
[ ] bitácora actualizada
[ ] DONE solo con evidencia
```

## 10. Regla de continuidad
El siguiente agente debe leer primero `BITACORA-ACR-XRAY.md`, después este documento, y solo entonces modificar archivos. Si se pierde el contexto conversacional, GitHub y estos dos documentos son el mapa de recuperación.
