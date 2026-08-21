# FORENSIC XRAY INVENTORY — 2026-08-21

## Estado
- Branch: `main`
- Tree/commit auditado: `aa36ca9df5e78cf0b0a0dd9753f190c4daddeba2`
- Método: GitHub Git Trees API, `recursive=1`
- Resultado: `truncated=false`
- Alcance: inventario estructural; NO se extrajeron ZIP en esta pasada.

## Hallazgo estructural
El árbol auditado contiene **46 entradas**: **45 blobs/archivos + 1 directorio (`PIPELINE/`)**. La entrada `PIPELINE/` contiene, en el árbol actualmente observado, `PIPELINE/00_METODO_TRABAJO_Y_ARQUITECTURA.md`.

## Archivos raíz/documentación y control
- `ACR-RECOVERY-PATCH-ANEXO-ACCESORIOS-INSTALACION.md` — 8,257 B
- `ACR-RECOVERY-PATCH-MAESTRO-OPENCLAW.md` — 19,220 B
- `ACR-RECOVERY-PATCH-ZIP.md` — 3,618 B
- `ACR-VERSION-MAP.md` — 3,328 B
- `AGENTS.md` — 41,396 B
- `BITACORA-ACR-XRAY.md` — 6,498 B
- `CLAUDE.md` — 9 B
- `CONTRIBUTING.md` — 19,185 B
- `DESIGN-cron-on-exit.md` — 3,503 B
- `LICENSE` — 1,170 B
- `RAIZ-OPENCLAW-COMO-HACER-TODO.md` — 7,669 B
- `README.md` — 87,369 B
- `SECURITY.md` — 35,445 B
- `THIRD_PARTY_NOTICES.md` — 1,575 B
- `VISION.md` — 5,986 B
- `PIPELINE/00_METODO_TRABAJO_Y_ARQUITECTURA.md` — 4,829 B

## Archivos de proyecto/configuración observados
- `Dockerfile` — 20,150 B
- `docker-compose.yml` — 5,580 B
- `fly.toml` — 773 B
- `render.yaml` — 449 B
- `appcast.xml` — 61,176 B
- `openclaw.mjs` — 23,463 B
- `package.json` — 116,016 B
- `pnpm-lock.yaml` — 442,086 B
- `pnpm-workspace.yaml` — 3,911 B
- `npm-shrinkwrap.json` — 132,212 B
- `taxonomy.yaml` — 650,803 B
- `tsconfig.core.json` — 339 B
- `tsconfig.core.projects.json` — 139 B
- `tsconfig.extensions.json` — 511 B
- `tsconfig.extensions.projects.json` — 151 B
- `tsconfig.json` — 13,052 B
- `tsconfig.plugin-sdk.dts.json` — 996 B
- `tsconfig.projects.json` — 144 B
- `tsdown.ai.config.ts` — 1,291 B
- `tsdown.config.ts` — 30,439 B
- `vitest.config.ts` — 241 B
- `CHANGELOG.md` — 2,956,571 B

## ZIP FORENSIC INVENTORY
Se localizaron **8 archivos ZIP** en la raíz. Tamaño total almacenado: **83,616,205 B (~79.74 MiB)**.

| Archivo | Tamaño | Blob SHA | Hallazgo |
|---|---:|---|---|
| `zip 1 openclaw-2026.7.1-2 parte 1.zip` | 16,411,464 B | `10527e5aaccefd2ed77e79f113a8e423f0a8282f` | DUPLICADO por blob SHA con ZIP 4 |
| `zip 4 openclaw-2026.7.1-2.zip` | 16,411,464 B | `10527e5aaccefd2ed77e79f113a8e423f0a8282f` | DUPLICADO por blob SHA con ZIP 1 |
| `zip 5 openclaw-2026.7.1-2 (2).zip` | 16,458,214 B | `eae8a785e120808c3d9a2b944e47fb9294d6b6f7` | Distinto |
| `zip 5.1 openclaw-2026.7.1-2.zip` | 10,027,045 B | `c1f0a4535dd06791722182b10cfff1392fb47e99` | Distinto |
| `zip 6 openclaw-2026.7.1-2.zip` | 10,035,035 B | `6963409b29cc00943ed1f13e5acf9f4a0cb69674` | Distinto |
| `zip 7 openclaw-2026.7.1-2.zip` | 2,405,790 B | `4b52c8569d6302052244fe347085c6c8ebab0d6b` | Distinto |
| `zip 8 openclaw-2026.7.1-2.zip` | 4,627,880 B | `04b81a76a0dbbd6625c0e6ed0193b0c1fbe82af6` | Distinto |
| `zip 9 open claw src.zip` | 7,239,313 B | `a3d442ef60c3e9638a8be3fc1c19c0bb03358bde` | Distinto; nombre indica `src` |

## Deducciones FORENSES — NO SON TODAVÍA CONCLUSIONES DE CONTENIDO
1. ZIP 1 y ZIP 4 son byte-idénticos a nivel de blob GitHub: mismo tamaño y mismo blob SHA.
2. Los otros 6 ZIP tienen blobs distintos; no se debe asumir que sean partes complementarias ni versiones equivalentes sin abrirlos.
3. Los nombres `zip 1`, `zip 4`, `zip 5`, `zip 5.1`, `zip 6`, `zip 7`, `zip 8`, `zip 9` sugieren un historial de intentos/segmentos, pero el nombre no demuestra contenido ni orden lógico.
4. La raíz actual contiene además una copia grande de `CHANGELOG.md` (2.96 MB), `taxonomy.yaml` (650.8 KB), `package.json` (116 KB) y `pnpm-lock.yaml` (442 KB). Su presencia no demuestra que correspondan al mismo ref que los ZIP.
5. No se debe eliminar ningún ZIP ni mover archivos todavía.

## SIGUIENTE PASADA FORENSE
Antes de extraer o desplegar:
1. Leer `ACR-RECOVERY-PATCH-ZIP.md` y el mapa de versión.
2. Obtener metadatos/bytes verificables de cada ZIP.
3. Determinar estructura interna de cada ZIP: carpeta envolvente, rutas, número de entradas y tamaños.
4. Calcular SHA-256 del archivo ZIP cuando los bytes estén disponibles fuera del API de Contents.
5. Comparar los árboles internos entre ZIP 1/4/5/5.1/6/7/8/9.
6. Identificar qué ZIP es fuente completa, qué ZIP es parcial y qué ZIP es duplicado.
7. Sólo después seleccionar el conjunto autorizado para reconstrucción OpenClaw.

**Regla:** esta auditoría no declara ningún ZIP como válido para despliegue hasta inspeccionar su contenido interno y compararlo con el ref oficial fijado.
