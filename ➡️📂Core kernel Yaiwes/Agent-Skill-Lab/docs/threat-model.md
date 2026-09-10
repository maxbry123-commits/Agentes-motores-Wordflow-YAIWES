# Threat Model

**Status:** initial, incomplete, and subject to review  
**Last updated:** 2026-07-28

## Security objective

Inspect and test untrusted agent skills without turning the inspection process into a
new execution, exfiltration, or supply-chain path.

## Assets to protect

- user files and repositories;
- credentials, tokens, environment variables, and keychains;
- network identity and private services;
- CI secrets and build infrastructure;
- integrity of reports and policy decisions;
- availability of the host running the inspector;
- privacy of proprietary skills;
- trust in published compatibility results.

## Potential adversaries

- a malicious skill author;
- an attacker who compromises a legitimate skill or dependency;
- a registry account impersonator;
- a malicious archive or repository crafted to exploit the inspector;
- an external analysis service that receives private content;
- a compromised scanner or plugin;
- a well-intentioned author whose skill has unsafe behavior;
- a model manipulated by prompt injection during semantic analysis.

## Trust boundaries

1. untrusted skill input entering the local inspector;
2. parser and filesystem traversal;
3. optional third-party scanner integration;
4. optional LLM or cloud analysis;
5. future behavioral sandbox;
6. CI environment and its secrets;
7. report consumption by humans and automation;
8. platform profiles and rule updates.

## Initial threats and mitigations

### T1 — Implicit execution during inspection

**Examples:** importing source modules, running package hooks, starting MCP servers,
rendering active content.

**Mitigations:**

- static MVP never imports or executes inspected content;
- parsers operate on bytes and bounded text;
- executable behavior is explicitly labeled and deferred;
- behavioral runs require a separate command and approval.

### T2 — Path traversal and symlink escape

**Examples:** `../` references, symlinks to credentials, recursive link loops.

**Mitigations:**

- resolve every path against a fixed inspection root;
- do not follow links outside the root;
- report links rather than silently traversing them;
- enforce file count, depth, and total size limits.

### T3 — Malicious archives and resource exhaustion

**Examples:** zip slip, decompression bombs, huge files, deeply nested metadata.

**Mitigations:**

- archives are outside the MVP;
- future archive handling uses bounded extraction into a disposable directory;
- enforce compression ratio, size, count, and path limits;
- use parser timeouts and bounded recursion.

### T4 — Parser exploitation

**Examples:** malicious YAML, encoding confusion, catastrophic regular expressions.

**Mitigations:**

- use safe parser modes;
- prohibit arbitrary object construction;
- normalize encodings explicitly;
- fuzz parsers and rule inputs;
- avoid unbounded regular expressions;
- keep parsing dependencies minimal and patched.

### T5 — Credential discovery or leakage

**Examples:** reading ambient environment values, uploading private skill content,
including secrets in reports.

**Mitigations:**

- baseline inspection does not read environment values;
- report variable names but never values;
- local operation is the default;
- remote engines require explicit opt-in and a data disclosure preview;
- redact known secret patterns from logs and reports.

### T6 — Prompt injection against semantic analysis

**Examples:** skill text instructs an analysis model to ignore policy or mark it safe.

**Mitigations:**

- deterministic checks remain authoritative for baseline facts;
- semantic analysis is optional and labeled as model-derived;
- treat skill text strictly as untrusted data;
- preserve raw evidence and model/tool version;
- never convert model output directly into execution permission.

### T7 — Compromised external scanner

**Examples:** malicious update, unexpected network use, unstable output schema.

**Mitigations:**

- integrations are optional;
- pin supported versions and verify release provenance where possible;
- preserve engine identity and raw results;
- run external engines with minimal privileges;
- do not merge findings in a way that hides their source.

### T8 — Report injection

**Examples:** skill content inserts terminal escapes, Markdown links, HTML, or forged
findings into the report.

**Mitigations:**

- escape untrusted terminal and markup content;
- separate evidence fields from report structure;
- mark quoted skill content clearly;
- test control characters, bidirectional text, and malicious filenames.

### T9 — False assurance

**Examples:** a green badge is interpreted as proof of safety.

**Mitigations:**

- avoid universal "safe" verdicts;
- list checks run, skipped, failed, and unsupported;
- distinguish declared, inferred, observed, and unknown facts;
- show tool versions and profile versions;
- document false-positive and false-negative limitations.

### T10 — Unsafe behavioral testing

**Examples:** sandbox escape, network exfiltration, host mounts, credential inheritance.

**Mitigations before release:**

- no behavioral runner in the MVP;
- separate reviewed threat model for execution;
- disposable environment with no ambient credentials;
- deny-by-default network and filesystem policies;
- explicit resource limits and process monitoring;
- human approval with exact execution plan;
- independent security review before general availability.

### T11 — Profile and rule supply-chain attack

**Examples:** a malicious compatibility update suppresses findings or authorizes new
capabilities.

**Mitigations:**

- profiles are version-controlled and code-reviewed;
- changes include fixtures and rationale;
- reports identify exact profile versions;
- future update channels use signed releases.

## Security properties required for the MVP

- no inspected file is executed;
- no network access is required;
- no environment values are collected;
- all filesystem reads stay within the selected root;
- outputs are deterministic for the same tool, profile, configuration, and input;
- findings contain inspectable evidence;
- malformed input fails closed with a clear error.

## Out of scope for the first model

- proving a skill is non-malicious;
- securing the target agent runtime itself;
- enforcing runtime permissions;
- validating remote registry identity;
- sandbox escape resistance;
- enterprise policy management.

These areas may become future scopes, but must not be implied by the MVP.

## Open questions

- Which capability categories can be inferred reliably from static content?
- How should conflicting platform permissions be normalized?
- Which artifacts must be hashed for reproducible reports?
- How can behavior be tested across proprietary runtimes without false equivalence?
- What independent review is required before enabling execution?
