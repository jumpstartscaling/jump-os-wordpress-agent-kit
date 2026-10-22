# Release process

## Release gate

Before a public tag:

1. Confirm `git status` is clean and `git diff --check` passes.
2. Run the complete Python test suite, Python compilation, and PHP syntax check.
3. Build the WordPress Bridge ZIP and inspect its contents to confirm it contains no `.env`, tenant policy, token, or private package.
4. Verify every README/doc link and every release asset checksum.
5. Update `CHANGELOG.md`, `VERSIONING.md` if necessary, and `docs/UPGRADING.md` for any public contract change.
6. Wait for the CI run for the exact release commit to complete successfully. A queued or unrelated green run is not release proof.
7. Publish a GitHub release with source provenance, SHA-256 checksums, compatibility status, upgrade notes, and known limits.

Build the public artifacts with:

```bash
python3 scripts/build_release_package.py --version X.Y.Z --output /safe/new/release-directory
```

Upload both ZIPs, `release-manifest.json`, and `SHA256SUMS.txt`. The script refuses an existing output directory and refuses to package a `.env` or a path under `private`.

## Release artifact rule

Public assets may contain only source-derived code, documentation, templates, checksums, and manifests. They must never contain generated private handoff packages, raw secrets, tenant names, provider logins, or production endpoint data.

## Release status vocabulary

- **Preview:** interfaces may change; provider claims remain documented-only or local-test evidence.
- **Candidate:** release gate passes; specific compatibility claims await independent provider verification.
- **Stable:** a versioned API contract with published evidence and upgrade policy.

The current project is pre-1.0 preview software. A GitHub release is a downloadable artifact, not a claim that every WordPress provider has independently verified it.
