# Fresh-Context PR Review Template

```text
Review this PR from a fresh context. Do not trust the author's summary.

Inputs:
- PR URL:
- Intended behavior:
- Out of scope:

Review passes:
1. Spec compliance: Does the diff implement the stated behavior and nothing surprising?
2. Correctness: Are edge cases handled?
3. Security/privacy: Any secrets, injection, permissions, auth, or data leaks?
4. Maintainability: Is the code simple and localized?
5. Verification: Were the right tests/checks run? Re-run key checks if possible.

Return:
- Blocking issues
- Non-blocking suggestions
- Verification commands run and results
- Final recommendation: approve / request changes / needs human decision
```
