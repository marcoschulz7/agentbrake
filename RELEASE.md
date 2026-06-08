# Releasing AgentBrake

The package is built, `twine check`-clean, and committed. Publishing is
outward-facing, so it needs *your* accounts — here are the exact steps.

## 0. Public identity (decided)

- Homepage: `https://agentbrake.dev`
- Repository: `https://github.com/marcoschulz7/agentbrake`

The PyPI project name `agentbrake` still needs to be free — check
https://pypi.org/project/agentbrake/ before the upload.

## 1. Push to GitHub — done via gh

```bash
gh repo create marcoschulz7/agentbrake --public --source=. --remote=origin --push
```

## 2. Publish to PyPI

Use TestPyPI first to see the page render, then the real index.

```bash
# build fresh artifacts
uv build                              # -> dist/agentbrake-0.1.0.tar.gz + .whl
uvx twine check dist/*                # must say PASSED for both

# dry run on TestPyPI (needs a TestPyPI token)
uvx twine upload --repository testpypi dist/*
pip install -i https://test.pypi.org/simple/ agentbrake   # smoke-test the install

# the real thing (needs a PyPI token)
uvx twine upload dist/*
```

After this, `pip install agentbrake` is live worldwide.

## 3. Tag the release

```bash
git tag -a v0.1.0 -m "AgentBrake 0.1.0"
git push origin v0.1.0
```

## Still open before/after launch

- **CrewAI live end-to-end run** with a real `OPENAI_API_KEY` (a few cents) —
  run `examples/crewai_quickstart.py` and watch a real crew get braked. The
  mechanics are verified against the real library; only the live run is left.
- Go-to-market — see `GO-TO-MARKET.md` (the $47k loop is the lead story).
- Landing page — see `WEBSITE-ARCHITECTURE.md`.
