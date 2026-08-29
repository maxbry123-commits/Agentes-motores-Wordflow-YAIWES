---
name: contrato-dag-sheriff
description: Convierte cada input en contrato DAG fail-closed. Use when the user pega contrato 1, pide INICIA, RUN, IMPUTA, input_block, sheriff, LOOP o skills grock tarea.
metadata:
  version: "2.4"
  type: recovery-patch
  mode: fail-closed+loop
  skill_url: https://github.com/maxbry123-commits/Agentes-motores-Wordflow-YAIWES/blob/main/tarea%20en%20curso%20grock%20gpt%20skills/skills%20grock%20tarea%201/SKILL.md
---

# Contrato DAG Sheriff

Leer `references/loop-engine.yml` y `assets/CONTRATO-1.yml` antes de emitir.

## Como trabajar

1. Leer contrato 1. Si falta, usar `assets/CONTRATO-1.yml`.
2. Partir el mensaje del Director en Ixx. Texto literal. Cero parafraseo.
3. Por cada Ixx abrir un nodo. Ejecutar `node_runtime` entero. Escribir el resultado de cada paso en el contrato 2. Prohibido escribir runtime ejecutado.
4. `out(Nn)` es el unico `in` legal de `Nn+1`.
5. Gap en un nodo activa LOOP de ESE nodo. Ver `references/loop-engine.yml`.
6. Emitir contrato 2 en chat. GitHub solo si el Director aprueba el path.
7. No RUN sin token INICIA o RUN o IMPUTA EL CONTRATO.

## Reglas

- R01 leer_literal
- R02 fuente_gana input_block > blob_sha > plan > chat
- R03 1 Ixx = 1 nodo
- R04 node_runtime escrito en contrato 2
- R05 ciclo PRELUDE RESEARCH BLOCK CODA por nodo
- R06 sin url o sha entonces P1 github+hf luego P2 skills OS luego P3 foros k=10
- R07 methods menor que 3 entonces LOOP
- R08 gap entonces LOOP BLOCK max 10 no escalar
- R09 i igual 10 entonces emitir gaps no PASS
- R10 sheriff FAIL entonces no siguiente
- R11 no RUN sin token
- R12 no REWRITE IMPROVE THIRD_STEP PASS_verbal OMIT_gap
- R13 PASS solo evidence
- R14 chat primero
- R15 path_default tarea en curso grock gpt skills/skills grock tarea 1/

## Lexicon

copia=COPY | fiel=DIFF | workflow=DISPATCH | audita=AUDIT | extraer=EXTRACT | lfs=STRIP_LFS | inicia=TOKEN | loop=LOOP

## node_runtime

Copiar este bloque dentro de cada nodo del contrato 2 y rellenarlo.

```yaml
in: {ixx, texto_literal, source:{url,sha}, prev_out}
PRELUDE: {F1,F2,F3}
RESEARCH: {P1[],P2[],P3[],methods10[]}
BLOCK_i:
  F4,F5,F6,F7,F8
  adversarial: [HIPOTESIS,EVIDENCIA+,ATAQUE,CONTRAEJEMPLOS,FUENTES-,RECALC_CONF]
  refute: [R1,R2,R3]
  vote: [RA,RB,RC,RD]
  plan_exec: [PLAN,EXECUTE,OBSERVE,SCORE,REFLECT,BRANCH]
  draft: [DRAFT,CRITIC,REFINE,CRITIC,REFINE,FINAL]
  think16: [T01..T16]
  operators: [ANALYZE,DECOMPOSE,INVESTIGATE,RETRIEVE,REFUTE,TRIANGULATE,CALIBRATE,WEIGH,FILTER,COMPARE,SIMULATE,VISUALIZE,CRYSTALLIZE,VERIFY,RECALL_MEMORY,UPDATE_CONTEXT]
CODA: {F9,F10}
out: {opcode, evidence[], score, verdict: PASS|FAIL|LOOP, next, gaps[]}
```

Si verdict=LOOP y i menor que 10 repetir BLOCK con gaps como input de investigacion. No pasar al siguiente nodo.

## Emit

Contrato 2 en chat. Campos minimos orden, input_block, nodos_con_runtime, gaps, veredicto, estado ESPERA_INICIA.
