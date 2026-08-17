# maxbry-router — Router inteligente (Cuenta A · Sistema)

Centro de control / routing del ecosistema MAXBRY / YAIWES.

## Método de trabajo — multi-cuenta

```
CUENTA A  maxbry123-commits
  agentes | maxbry-router (este) | osquestador-auditor | MEMORIA
        │
        │ credential_ref
        ▼
CUENTA B  almacén de software (forks/tools) — solo lectura/download
HF        datasets / models / skills grandes
RUNTIME   ejecución tras adquisición
```

El Router **no embebe** software externo. Resuelve capacidades y delega adquisición al motor del Wordflow (`agentes`) con el mismo `AccountRegistry` / `credential_ref`.

### Referencias canónicas

- Método: https://github.com/maxbry123-commits/agentes/blob/main/PIPELINE/53_MULTI_ACCOUNT_STORAGE_METHOD.md
- Conector Cuenta B: https://github.com/maxbry123-commits/agentes/blob/main/extensions/wordflow/connectors/github_external.py
- Kernel Wordflow: https://github.com/maxbry123-commits/agentes/tree/main/extensions/wordflow_kernel

### Seguridad

- Nunca token en código ni README.
- Rutas declarativas con `task_id` / `trace_id` cuando aplique.
- LLM / providers solo detrás del contrato del router, no desde el loop del Wordflow en directo.
