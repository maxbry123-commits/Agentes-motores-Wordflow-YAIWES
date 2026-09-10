# Aspire Dashboard Tracing Sample

This sample demonstrates how to configure observability for Azure AI Foundry agents using OpenTelemetry and the Aspire Dashboard.

## Prerequisites

- Python 3.10 or higher
- Azure AI Foundry project
- Docker (for running Aspire Dashboard locally)

## Setup

### 1. Install Dependencies

Install the required packages including the OTLP exporter:

```bash
pip install agent-framework-foundry -U
pip install opentelemetry-exporter-otlp-proto-grpc
```

### 2. Start Aspire Dashboard

Run the Aspire Dashboard locally using Docker:

```bash
docker run --rm -it -d \
    -p 18888:18888 \
    -p 4317:18889 \
    --name aspire-dashboard \
    mcr.microsoft.com/dotnet/aspire-dashboard:latest
```

This will start:
- **Web UI**: http://localhost:18888
- **OTLP endpoint**: http://localhost:4317

### 3. Configure Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Update the values in `.env`:

```env
FOUNDRY_PROJECT_ENDPOINT="https://your-project.services.ai.azure.com"
FOUNDRY_MODEL="gpt-4o-mini"
ENABLE_INSTRUMENTATION=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

### 4. Authenticate with Azure

```bash
az login
```

## Running the Sample

```bash
python simple.py
```

The sample will:
1. Configure OpenTelemetry providers based on environment variables
2. Create an agent with a weather tool
3. Process multiple questions
4. Send telemetry data to Aspire Dashboard

## Viewing Telemetry

1. Open the Aspire Dashboard at http://localhost:18888
2. Navigate to the "Traces" section
3. Look for traces with the ID printed in the console
4. Explore the distributed traces showing:
   - Chat completions
   - Tool executions
   - Token usage
   - Timing information

## Key Features

- **Standard OpenTelemetry**: Uses standard `OTEL_EXPORTER_OTLP_*` environment variables
- **Automatic Instrumentation**: Agent Framework automatically instruments agent operations
- **Distributed Tracing**: See end-to-end traces across agent and tool calls
- **Token Metrics**: Track token consumption and costs

## Troubleshooting

### No telemetry data appearing

1. Verify Aspire Dashboard is running: `docker ps`
2. Check `ENABLE_INSTRUMENTATION=true` in your `.env` file
3. Ensure `OTEL_EXPORTER_OTLP_ENDPOINT` points to the correct endpoint

### Import errors

If you see `ModuleNotFoundError: No module named 'opentelemetry.exporter'`, install the OTLP exporter:

```bash
pip install opentelemetry-exporter-otlp-proto-grpc
```

## Additional Resources

- [Agent Framework Observability Documentation](https://github.com/microsoft/agent-framework/tree/main/python/samples/02-agents/observability)
- [Aspire Dashboard Documentation](https://learn.microsoft.com/en-us/dotnet/aspire/fundamentals/dashboard/standalone)
- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/languages/python/)
