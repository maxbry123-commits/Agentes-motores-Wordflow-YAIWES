# Security policy

## Supported version

Security fixes are applied to the current default branch.

## Reporting

Please report a suspected vulnerability privately through GitHub Security Advisories. Do not include real credentials, official competition data, private service endpoints, or proprietary artifacts in a public issue.

## Public-data boundary

This repository must never contain:

- API keys, tokens, SSH keys, registry credentials, or private endpoints;
- internal server addresses, user-specific absolute paths, or image digests;
- official test inputs, predictions, model checkpoints, raw competition logs, or submission archives;
- third-party source, weights, or datasets without an explicit redistribution basis;
- reconstructed traces presented as original logs.

If any of these appear, treat the incident as a release-boundary failure: remove the material from the public branch, rotate affected credentials where applicable, and document the correction without republishing the sensitive value.

## Scope

This policy covers only this personal public repository. It does not authorize access to any external system, dataset, service, or historical competition artifact.
