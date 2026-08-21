# ROOTS — espacio de raíces de agentes

Este repositorio es multi-agente/multi-motor. `ROOTS/` reserva un espacio aislado para cada agente o motor recuperado.

## Regla estructural
Cada agente ocupa su propia raíz:

```text
ROOTS/
├── openclaw/
├── <agente-02>/
├── <agente-03>/
└── ...
```

La raíz interna de cada agente conserva sus rutas relativas originales. No se mezclan archivos entre agentes.

## OpenClaw
`ROOTS/openclaw/` será construido únicamente después de la verificación cruzada contra:

- `openclaw/openclaw@a4178c7eb15a0dd2b8b44804348e256f1a109a34`
- ZIP(s) candidatos extraídos
- manifiesto de raíz
- read-back de GitHub

No se copiarán dependencias generadas (`node_modules`, `.pnpm-store`, `dist`, `build`, `coverage`, caches, logs, credenciales o temporales).

## Documentación y control
La bitácora, Recovery Patch, inventarios, pipelines y manifiestos permanecen fuera de las raíces de agentes para no contaminar los árboles fuente.

## Regla de integridad
No mover archivos OpenClaw existentes a `ROOTS/openclaw/` hasta que la auditoría T06/T08 determine que cada archivo tiene una fuente y una ruta de destino verificables.
