# Bitácora LOOP — auditoría final OpenClaw

Fecha: 2026-08-21

## Regla de trabajo
No declarar 100% hasta cruzar la raíz contra el ref canónico oficial, la guía de instalación desde source y las superficies workspace/UI/extensions/packages/examples. Separar diferencias de contenido de diferencias causadas por ZIP, symlinks, modos y artefactos generados.

## Fuente canónica
OpenClaw oficial: `openclaw/openclaw`
Ref objetivo: `a4178c7eb15a0dd2b8b44804348e256f1a109a34`

## Hallazgos confirmados
1. `ROOTS/openclaw/package.json` coincide con el archivo oficial por SHA `b5dc6a51d61774a8bfe8a6d468890cba3bda1513`.
2. `ROOTS/openclaw/ui/package.json` coincide con oficial por SHA `2df258047362e95422895ed3a2a95b8d32abbbc6`.
3. `ROOTS/openclaw/extensions/telegram/package.json` coincide con oficial por SHA `387c09b1c63bfdd09aabd70b1f9d693fbbc95de4`.
4. `ROOTS/openclaw/packages/gateway-client/package.json` coincide con oficial por SHA `79af62c9f5638d975ee36fe7165dc54398040fa7`.
5. `ROOTS/openclaw/examples/ai-chat` coincide con el directorio oficial por el mismo SHA de árbol `674504691fbae16d580e36999ca82689687910bc`.
6. `pnpm-workspace.yaml`, `node-version.mjs` y `openclaw.mjs` fueron verificados anteriormente contra el ref canónico.
7. Hallazgo crítico: `ROOTS/openclaw/pnpm-lock.yaml` no estaba presente en `main`. El repositorio oficial sí contiene `pnpm-lock.yaml`; la documentación oficial lo usa para instalaciones reproducibles desde source/Docker.
8. El workflow final fue modificado para restaurar exclusivamente ese lockfile desde el ref canónico y verificar SHA de archivos críticos.
9. El PR final de auditoría #10 fue creado para ejecutar el workflow PR-triggered, pero GitHub no mostró un workflow run asociado al commit consultado. Por tanto, NO se declara finalización 100%.
10. La documentación oficial actual indica desde source: `pnpm install`, `pnpm build`, `pnpm ui:build`, y luego `pnpm link --global`/onboarding; también confirma que `pnpm` es necesario para builds desde source.
11. La documentación oficial actual indica Node soportado 22.22.3+, 24.15+ o 25.9+, con Node 26 recomendado actualmente; esto reemplaza cualquier supuesto antiguo de versión.
12. La documentación de Control UI confirma que `pnpm ui:build` genera los assets servidos desde `dist/control-ui`.

## Regla de exclusión
No subir `node_modules`, `.pnpm-store`, `dist`, `build`, `coverage`, `.cache` ni `logs` como dependencias/artefactos generados de la raíz fuente.

## Estado
Raíz canónica publicada: SÍ.
Comparación crítica de código fuente: PARCIALMENTE VERIFICADA.
Lockfile canónico: DETECTADO COMO FALTANTE Y PENDIENTE DE CONFIRMACIÓN DE ESCRITURA.
Workflow final: PREPARADO.
Auditoría X-Ray 100%: NO DECLARADA.

## Próximas tareas obligatorias
1. Obtener evidencia de ejecución real del workflow final.
2. Confirmar presencia de `ROOTS/openclaw/pnpm-lock.yaml` en `main`.
3. Comparar SHA del lockfile con el oficial.
4. Completar comparación de árbol completo.
5. Auditar symlinks/modos independientemente del contenido ZIP.
6. Verificar comandos de instalación/build/UI contra la raíz.
7. Auditar extensiones completas y workspace.
8. Verificar ausencia de artefactos generados.
9. Actualizar auditoría X-Ray final.
10. Solo entonces declarar 100%.
