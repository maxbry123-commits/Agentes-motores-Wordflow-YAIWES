# Corpus Admission Report 001

**Date:** 2026-07-28  
**Scope:** Phase 0 corpus pinning and licensing  
**Execution:** none

## Outcome

Twelve public skill packages were admitted for static research.

For every admitted sample, the project recorded:

- immutable repository commit and commit date;
- exact skill root;
- Git tree identity;
- SHA-256 of the complete `git ls-tree` inventory;
- complete relative file list, modes, and blob identities;
- `SKILL.md` blob identity;
- applicable license evidence;
- selection rationale and expected features.

The complete records are in:

- [`corpus.yml`](corpus.yml)
- [`inventories.yml`](inventories.yml)

## Summary

| Measure | Result |
|---|---:|
| Admitted skill packages | 12 |
| Source repositories | 6 |
| Inventoried files | 103 |
| Replaced candidates | 3 |
| Packages containing executable-mode files | 4 |
| Executable-mode files | 11 |
| Packages containing symlinks | 1 |
| Submodules inside selected roots | 0 |
| Skills installed or executed | 0 |

## License distribution

| License | Samples | Notes |
|---|---:|---|
| Apache-2.0 | 3 | Skill-scoped license files |
| MIT | 8 | Repository license, sometimes repeated in skill metadata |
| CC-BY-4.0 | 1 | Attribution obligations apply |

This is a project intake record, not legal advice.

## Candidate replacements

Three original Anthropic candidates were not admitted:

### `template-skill`

No skill-level license or clear scoped open-source grant was found. Public readability
was not treated as permission to copy or reuse.

**Replacement:** `skill-creator`, which includes an Apache-2.0 license.

### `doc-coauthoring`

No skill-level license or clear scoped open-source grant was found.

**Replacement:** `mcp-builder`, which includes an Apache-2.0 license.

### `pptx`

Its skill-specific license restricts retaining, reproducing, modifying, and
distributing the material outside authorized Anthropic service use.

**Replacement:** `webapp-testing`, which includes an Apache-2.0 license.

No contents from the excluded packages are included in this repository.

## Structural observations

### Complete package identity matters

The 12 `SKILL.md` files represent only part of the admitted material. The complete
corpus contains 103 files, including scripts, references, examples, fixtures,
evaluations, signatures, and governance material.

Hashing only `SKILL.md` would not reproduce the inspected package.

### Symlinks require an explicit policy

The OpenClaw `autoreview` package contains one symlink:

```text
CLAUDE.md -> AGENTS.md
```

The target remains inside the selected skill root. It is admitted, but provides a
useful positive fixture for path-boundary checks.

### Package shapes vary substantially

The corpus ranges from one-file instructional skills to an 18-file authoring system
and a 36-file reference package. A validator must not assume that a skill is only a
single Markdown file.

### Governance artifacts are not universal

The NVIDIA sample contains a signature, skill card, evaluation dataset, and benchmark.
These artifacts should be recognized without becoming mandatory for every platform.

## Safety record

The source repositories were read through shallow, bare Git clones with submodule
recursion disabled. Analysis used Git object and tree inspection only.

- No working tree was checked out.
- No dependency was installed.
- No package hook ran.
- No script or skill instruction was executed.
- No third-party skill content was copied into this repository.
- Temporary source clones are not research deliverables.

## Admission decision

All 12 replacement-adjusted samples satisfy the Phase 0 admission requirements for
static analysis.

Admission does not mean that a skill is safe, compatible, correct, or endorsed. It
means only that its source identity, package boundary, inventory, and research-use
license evidence are documented well enough to proceed to manual static baselining.

## Next step

Create versioned manual compatibility baselines for the admitted corpus before running
external scanners.
