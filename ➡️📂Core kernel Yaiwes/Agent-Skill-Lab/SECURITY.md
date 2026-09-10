# Security Policy

## Project status

Agent Skill Lab is currently in discovery and specification. There are no supported
binary or package releases yet.

## Reporting a vulnerability

Please do not publish exploit details in a public issue.

Use GitHub's private vulnerability reporting option in the repository **Security**
section when it is available. If private reporting is unavailable, contact the
maintainer through the GitHub profile and ask for a private reporting channel without
including sensitive details in the first message.

Include, when possible:

- affected commit or version;
- operating system and runtime;
- minimal reproduction steps;
- expected and observed behavior;
- potential impact;
- whether the issue is already public.

## Response principles

Maintainers will:

- acknowledge a valid private report as soon as practical;
- avoid requesting secrets or unrelated personal information;
- reproduce issues in an isolated environment;
- coordinate disclosure timing with the reporter;
- credit reporters who want public attribution;
- publish remediation and limitations with the fix.

## Security promises and limitations

Agent Skill Lab will use best-effort analysis. A report with no findings is not proof
that a skill is safe.

Reports must identify:

- the tool and version that produced them;
- the checks that ran;
- checks that were skipped or failed;
- evidence for each finding;
- unresolved uncertainty;
- whether any content was executed.

See [docs/threat-model.md](docs/threat-model.md) for the current threat model.
