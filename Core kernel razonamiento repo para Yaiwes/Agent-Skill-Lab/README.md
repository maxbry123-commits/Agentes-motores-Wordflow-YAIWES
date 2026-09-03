# Agent Skill Lab

An open-source, vendor-neutral test lab for AI agent skills.

> **Project status:** v0.1 scope definition. No executable release exists yet.

Agent Skill Lab aims to help skill authors and users answer four practical questions:

1. Is this skill structurally valid?
2. Which agent platforms can use it, and with what changes?
3. What capabilities and permissions does it appear to require?
4. Does it behave consistently with its declared purpose?

The project is not intended to be another generic malware scanner. Existing security
scanners already cover that problem from several angles. Agent Skill Lab will focus on
portable validation, compatibility profiles, explicit capability manifests, and
reproducible behavioral tests. Security scanners may later be integrated as optional
engines.

## Why this project?

Agent skills can contain instructions, scripts, references, and assets. They are
increasingly portable, but different runtimes still add their own conventions,
metadata, tools, and execution boundaries. A skill that parses correctly is not
necessarily portable, reliable, or safe to run.

Agent Skill Lab proposes a common workflow:

```text
inspect -> validate -> describe capabilities -> test -> report
```

## Planned first release

The proposed v0.1 is intentionally limited. It will:

- inspect a local skill directory without executing its contents;
- validate the core Agent Skills structure and metadata;
- apply target-specific compatibility profiles;
- produce an explicit capability and permission report;
- explain findings in human-readable language;
- export deterministic Markdown and JSON reports;
- run locally without uploading the skill.

See [Version 0.1 Scope](docs/v0.1-scope.md), [Product Scope](docs/product-scope.md),
and [Roadmap](ROADMAP.md).

## Initial compatibility targets

- Agent Skills open format
- OpenClaw / ClawHub
- Hermes Agent

NanoClaw, Codex, Claude Code, and other runtimes are deferred. The three listed
profiles are planned validation targets, not a claim of current support. See the
[Compatibility Model](docs/compatibility-model.md).

## Principles

- **Vendor-neutral:** no platform owns the core model.
- **Local-first:** source code stays on the user's machine by default.
- **Evidence over badges:** reports show evidence and uncertainty instead of making
  absolute safety claims.
- **No implicit execution:** untrusted skill code is never executed during static
  inspection.
- **Deterministic core:** the baseline report must not require an LLM.
- **Human control:** consequential actions require explicit approval.
- **Composable security:** established scanners should be integrated rather than
  unnecessarily reimplemented.
- **Open development:** decisions, limitations, and tests remain reviewable.

## Documentation

- [Vision](VISION.md)
- [Version 0.1 Scope](docs/v0.1-scope.md)
- [Product Scope](docs/product-scope.md)
- [Competitive Landscape](docs/competitive-landscape.md)
- [Threat Model](docs/threat-model.md)
- [Compatibility Model](docs/compatibility-model.md)
- [Decision 0001: Product Direction](docs/decisions/0001-product-direction.md)
- [Roadmap](ROADMAP.md)
- [Portuguese summary](README.pt.md)

## Research

Phase 0 research is tracked openly under [`research/`](research/README.md). Three
manual baselines and a pinned SkillSpector comparison confirmed a narrow offline
compatibility gap. The remaining broad corpus work is paused in favor of the v0.1
rule proof.

## Contributing

The project is currently documentation-first. Research corrections, test cases, and
design feedback are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before
proposing implementation work.

## Security

No scanner can prove that an arbitrary skill is safe. Agent Skill Lab will report what
was checked, what was observed, and what remains unknown. See [SECURITY.md](SECURITY.md)
and the [Threat Model](docs/threat-model.md).

## License

[MIT](LICENSE)
