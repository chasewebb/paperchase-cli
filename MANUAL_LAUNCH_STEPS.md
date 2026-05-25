# Manual Launch Steps — v0.1.0 Pre-Tag Checklist

The Phase 3 CI/release pipeline is wired up, but a few one-time human actions
must happen **before** tagging `v0.1.0`. Tagging without these will cause the
`release.yml` workflow to fail.

---

## 1. Reserve the PyPI package name

1. Open https://pypi.org/manage/projects/ (log in as the owner).
2. Search for `paperchase`.
3. If available — proceed. If taken, fall back to `paperchase-cli` and update
   `[project] name` in `pyproject.toml` accordingly (also update
   `homebrew-tap/Formula/paperchase.rb` URLs).

## 2. Configure PyPI trusted publishing (no token required)

PyPI uses OIDC trusted publishing — no API token is stored anywhere. Configure
it once on PyPI:

1. Go to https://pypi.org/manage/account/publishing/
2. Add a new pending publisher:
   - PyPI Project Name: `paperchase` (or `paperchase-cli` if the fallback)
   - Owner: `chasewebb`
   - Repository: `paperchase-cli`
   - Workflow filename: `release.yml`
   - Environment name: *(leave blank)*
3. Save. After the first successful publish PyPI flips it from "pending" to
   "active" automatically.

## 3. Reserve the npm package names

1. Open https://www.npmjs.com/ (log in as the owner).
2. Verify both `paperchase` (the npx shim) and the `@paperchase` org / scope
   for `@paperchase/mcp` are available.
3. If `paperchase` is taken, fall back to `@paperchase/cli` and update
   `npx-shim/package.json` "name" field.
4. Create the `@paperchase` org on npm if it does not exist yet (one-click
   from the npm dashboard).

## 4. Generate an npm publish token + add to repo secrets

1. https://www.npmjs.com/settings/<user>/tokens → "Generate New Token" →
   choose **Automation** (or "Granular" scoped to the two package names).
2. Copy the token (`npm_xxx...`).
3. Add it to the repo:

   ```bash
   gh secret set NPM_TOKEN -R chasewebb/paperchase-cli --body "npm_xxx..."
   ```

## 5. Generate a GitHub PAT with Homebrew tap write + add to repo secrets

The `homebrew-bump` job opens a PR against the `homebrew-tap/` directory
(which the spec keeps inside this repo, but the bump action needs write
permission to push a branch).

1. https://github.com/settings/personal-access-tokens/new → fine-grained PAT
   scoped to `chasewebb/paperchase-cli` (or a separate tap repo if the tap is
   moved out later). Permissions needed:
   - Contents: Read and write
   - Pull requests: Read and write
   - Metadata: Read-only
2. Copy the token (`github_pat_xxx...`).
3. Add it to the repo:

   ```bash
   gh secret set HOMEBREW_TAP_TOKEN -R chasewebb/paperchase-cli --body "github_pat_xxx..."
   ```

## 6. (Optional) Smoke-test on TestPyPI first

If paranoid, temporarily edit `.github/workflows/release.yml` to point the
PyPI publish action at TestPyPI:

```yaml
- uses: pypa/gh-action-pypi-publish@release/v1
  with:
    repository-url: https://test.pypi.org/legacy/
```

Tag a `v0.1.0-rc.1` and verify TestPyPI shows the wheel before reverting and
tagging the real `v0.1.0`.

---

## After all six steps are done — Phase 5 is unblocked

```bash
git tag v0.1.0 -m "PaperChase v0.1 — Claude-Code-style REPL + Hermes-class autonomous loop, MIT"
git push origin v0.1.0
gh run watch -R chasewebb/paperchase-cli
```

Expected jobs all green: `pypi`, `npm-shim`, `npm-mcp`, `rust-binaries`,
`homebrew-bump`.
