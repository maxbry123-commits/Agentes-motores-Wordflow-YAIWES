# Parte 03 — packages/

`packages/**` se conserva inicialmente completo porque contiene paquetes internos del runtime, agente, gateway, protocolo, LLM, media, SDK y contratos de plugins.

Prioridad: CRÍTICA

ACR debe resolver referencias `workspace:*` y dependencias internas antes de excluir cualquier paquete.

Estado ACR: preparado para segmentación y transferencia recuperable.
