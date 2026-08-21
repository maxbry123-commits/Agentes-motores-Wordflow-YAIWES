# ACR LOOP trigger

This file exists only to trigger the GitHub Actions ZIP XRAY extraction workflow after the workflow definition is committed and verified. It is control metadata, not OpenClaw source.

Trigger purpose: acquire actual ZIP bytes inside GitHub Actions, validate archives, extract them preserving relative paths, generate manifests, and upload reproducible extraction artifacts.
