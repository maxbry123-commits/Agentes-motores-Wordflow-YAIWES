---
type: containerization_protocol
version: 1
status: active
updated: 2026-07-18
project: Agent_Handoff
---

# Containerization Protocol

## Purpose

This protocol defines how Agent Handoff projects choose, document, change, and verify Docker and Docker Compose organization.

Agent Handoff does not impose one universal container file layout. The layout is a project decision controlled by the user or maintainer.

## Mandatory user decision gate

This decision gate applies in both cases:

1. initializing Agent Handoff in a new repository;
2. adding Agent Handoff to an existing repository.

The agent MUST ask the user a separate, explicit containerization question before creating, moving, renaming, deleting, or consolidating Dockerfiles, Compose files, container scripts, build contexts, environment-file references, or container configuration.

The agent MUST NOT infer approval from the presence or absence of existing Docker files, from general best practices, or from the recommended default in this document.

### Required questions

Ask the user to confirm:

1. whether Docker or Docker Compose is used now or planned;
2. which supported layout should be used;
3. for an existing repository, whether the current layout must be preserved or may be migrated;
4. which development, test, and production entry commands are canonical;
5. whether production deployment configuration belongs in this repository or in a separate deployment repository.

A concise question is acceptable, but the containerization decision must not be hidden inside a broader initialization or migration question.

### When the user has not answered

For a new repository, do not create container infrastructure and record the choice as unresolved.

For an existing repository, preserve the current layout and do not relocate or consolidate container files. Non-container Agent Handoff files may still be added when that work is otherwise safe.

## Supported approaches

### 0. No repository-managed containerization

Use this when Docker is not required or container execution is managed entirely outside the repository.

Do not create placeholder Dockerfiles or Compose files without an approved use case.

### 1. Colocated service files

Store each Dockerfile next to the source code and keep the primary Compose entry point at the repository root.

```text
repository/
├── compose.yaml
├── compose.dev.yaml
├── service-a/
│   ├── Dockerfile
│   └── src/
└── service-b/
    ├── Dockerfile
    └── src/
```

Use this for small repositories and services whose image definition changes together with application dependencies and source layout.

Strengths:

- short and predictable build paths;
- Dockerfile ownership is close to service ownership;
- simple root-level Compose commands.

Trade-off:

- container-related files are distributed across service directories.

### 2. Centralized `docker/` directory

Store Compose files, Dockerfiles, container scripts, initialization assets, and shared configuration under `docker/`.

```text
repository/
├── application/
│   └── src/
├── docker/
│   ├── compose.yaml
│   ├── compose.dev.yaml
│   ├── compose.prod.yaml
│   ├── application/
│   │   └── Dockerfile
│   ├── postgres/
│   │   └── init/
│   └── scripts/
└── .env.example
```

Use this when container infrastructure is substantial and centralized discoverability is more valuable than proximity to service code.

Strengths:

- one discoverable location for container infrastructure;
- a cleaner repository root;
- convenient for shared scripts and configuration.

Trade-offs:

- more relative paths;
- commands often require `-f docker/compose.yaml` or a wrapper command;
- a parent build context may expose more of the repository to the build than required.

### 3. Hybrid layout

Keep primary Compose entry points at the repository root, service Dockerfiles next to their source, and shared container infrastructure under `docker/`.

```text
repository/
├── compose.yaml
├── compose.dev.yaml
├── compose.prod.yaml
├── service-a/
│   ├── Dockerfile
│   └── src/
└── docker/
    ├── configs/
    ├── postgres/init/
    └── scripts/
```

This is the recommended default to present to users for small and medium multi-service repositories. It MUST NOT be selected without user confirmation.

Strengths:

- simple root-level Compose commands;
- Dockerfiles remain close to service code;
- shared infrastructure has a dedicated location.

Trade-off:

- container infrastructure is intentionally split between the root, services, and `docker/`.

### 4. Modular monorepo layout

Keep Dockerfiles and optional service-level Compose modules inside each service, with a documented top-level orchestration entry point.

```text
repository/
├── compose.yaml
├── services/
│   ├── api/
│   │   ├── Dockerfile
│   │   └── compose.yaml
│   └── worker/
│       ├── Dockerfile
│       └── compose.yaml
└── docker/
    └── shared/
```

Use this when services have independent ownership, release cycles, or local development workflows.

The repository must document whether top-level orchestration uses Compose `include`, multiple `-f` files, generated configuration, or another explicit mechanism.

Strengths:

- service autonomy;
- smaller service-specific contexts;
- easier ownership in a growing monorepo.

Trade-offs:

- orchestration and path resolution become more complex;
- duplicate configuration can appear without clear shared conventions.

### 5. Separate deployment repository

Keep application image definitions with application code while storing production deployment orchestration in a separate repository.

Use this when application and operations ownership are separated, deployment configuration has a different release lifecycle, or production access boundaries require repository separation.

The application repository must link to the deployment repository without copying secrets or environment-specific private values.

Strengths:

- clear application and deployment ownership boundaries;
- independent release and access controls.

Trade-offs:

- cross-repository coordination is required;
- a clone of one repository may not contain the complete production deployment state.

### 6. Preserve an existing or custom layout

An established repository may retain a layout not listed above.

Preservation is preferred over unnecessary migration when the current structure is understandable, documented, and testable.

A custom layout must document:

- the reason for the layout;
- canonical entry commands;
- build contexts and Dockerfile locations;
- ownership of shared scripts and configuration;
- known path-resolution constraints.

## Selection guidance

| Project condition | Typical choice |
|---|---|
| Docker is not used | No repository-managed containerization |
| One or a few services | Colocated or hybrid |
| Substantial shared Docker infrastructure | Centralized or hybrid |
| Growing monorepo with service ownership | Modular monorepo |
| Separate application and operations ownership | Separate deployment repository |
| Mature existing repository | Preserve existing unless migration is explicitly approved |

This table guides the user conversation. It does not authorize the agent to choose on the user's behalf.

## Common requirements

For every repository-managed containerization approach:

- build contexts and Dockerfile paths must be explicit;
- build contexts should be no broader than required;
- each build context must have an appropriate `.dockerignore` or Dockerfile-specific ignore file;
- primary development, test, production, build, stop, and log commands must be documented when applicable;
- real secrets and production environment files must not be committed;
- `.env.example` or equivalent documentation should describe required non-secret variables;
- ports, volumes, networks, profiles, dependencies, and health checks must be understandable from repository documentation;
- generated Compose configuration should not become an undocumented source of truth;
- wrapper commands such as Make, Task, Just, or repository scripts may be used, but their underlying Compose files and order must remain discoverable.

## Compose path and override rules

The project must document:

- the primary Compose file;
- the project directory used for relative paths;
- the order of multiple `-f` files;
- whether `include`, profiles, or overrides are used;
- the location and purpose of each `env_file`;
- the method used to provide variables for Compose interpolation;
- any paths that intentionally reference files outside the Compose directory.

Agents must inspect these rules before changing relative paths, volumes, build contexts, or environment-file references.

## Migration rules

Migration between layouts requires explicit user approval.

Before migration:

1. inventory Dockerfiles, Compose files, ignore files, scripts, configuration, volumes, environment references, CI commands, and documentation;
2. identify consumers outside the repository, including deployment automation and developer scripts;
3. define the target layout and canonical commands;
4. keep the migration in a focused Issue, branch, and Pull Request;
5. avoid unrelated application refactoring in the same migration;
6. provide compatibility wrappers when removing them immediately would break documented workflows.

## Verification

When Docker or Compose configuration changes, run the applicable checks:

1. render and validate the effective Compose model with `docker compose config`;
2. build the affected images or document why building was not possible;
3. start the affected services or run a focused container smoke test;
4. verify health checks, required ports, volumes, and service dependencies;
5. verify that ignored and secret files are not unintentionally included in build contexts or commits;
6. verify canonical commands from the documented repository entry point.

If a check cannot be run, record the reason, risk, and next action in the Issue, Pull Request, or handoff.

## Project memory

Record the confirmed current layout and canonical commands in `ai/PROJECT_STATE.md`.

Record a new layout choice or approved migration in `ai/DECISIONS.md` when it is a durable project decision.

A handoff for container work should state:

- selected layout;
- files and paths changed;
- commands run;
- effective Compose files and order;
- images or services tested;
- changed ports, volumes, networks, health checks, or environment variables;
- unresolved risks and rollback or compatibility notes.
