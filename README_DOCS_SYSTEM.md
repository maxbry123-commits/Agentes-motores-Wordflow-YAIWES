# Nota — Sistema de documentos (Router)

**Subida:** carpeta `reception/` → Upload file → commit.

**Regla:** Sin Context + método de trabajo + Handoff verificado → el agente **no** programa ni declara auditoría válida.

```yaml
HANDOFF_RULE:
  handoff_is_not_full_traceability: true
  if_missing: BLOCK
```

Schema: `reception/DOC_UPLOAD_SCHEMA.yaml`  
Método global: agentes/PIPELINE/
