# shared/prompts/

Shared prompt fragments reused across skills.

| File | Where it's inserted |
|---|---|
| `nda-instruction.md` | Into every prompt — a reminder about confidentiality and anonymization. |
| `verbatim-policy.md` | Into skills that generate quotes (`07-quick-summary`, `17-key-findings`, `18-report-draft`). |
| `qualitative-vs-quantitative.md` | Into analytical skills — a reminder not to use percentages. |
| `fact-vs-interpretation.md` | Into analysis and report skills. |

A skill pulls the fragment it needs into its own prompt via include or plain copy-paste — different backends use different templating mechanisms.
