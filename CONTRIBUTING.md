# Contributing to Ableton-AI-Stemcell-Skill

Thanks for your interest! This is a hobby project — issues, ideas, and PRs are all welcome.

## Development setup

```bash
git clone https://github.com/zayansalman/ableton-ai-stemcell-skill.git
cd ableton-ai-stemcell-skill
uv sync
uv run stemcell bootstrap   # downloads the models (once)
uv run python -m pytest -q  # run the tests
uv run stemcell selftest    # offline synthetic end-to-end check
```

Python 3.11 (basic-pitch's ceiling). The lockfile is pinned to `darwin/arm64`; if you're porting to another platform, relax `[tool.uv].environments` in `pyproject.toml` and expect to re-solve torch.

## Architecture

Each pipeline stage is a module in `src/stemcell/` exposing a single `run(ctx: Ctx) -> None` that reads prior-stage outputs from `ctx.outdir` and writes its own. The `Ctx` dataclass (`ctx.py`) is the contract; `report.json` (schema v1) is the authoritative output. See [`docs/architecture.md`](docs/architecture.md).

Stages: `ingest → separate → analyze → drums → transcribe → report`. Standalone generators: `melody.py` (hooks), `vocalchop.py` (chops).

## Ground rules

- **No silent quality caps.** If you bound coverage (top-N, sampling, a cap like `MAX_TODD_SLICES`), surface it to the user.
- **Honest epistemics.** Gear/sound identification is inference. Keep the documented-vs-lore distinction the knowledge bases in `references/` are careful about. Never present a guess as fact.
- **Verify on real audio.** The offline `selftest` sets `skip_clap=True` and can't catch model-path bugs — run a real `stemcell run` and `stemcell chop` before claiming a change works.
- **Match the surrounding style.** Small, direct, type-hinted; comment the non-obvious *why*, not the *what*.

## Adding a knowledge base

The `references/*.md` files (gear fingerprints, vocal-chop craft) are built by parallel web research + an adversarial fact-check pass, with every risky claim tagged. If you extend them, keep that discipline and cite sources.

## Reporting issues

Include the command you ran, the `report.md` (or the traceback), your OS/chip, and the model versions (`uv pip list | grep -E 'demucs|basic-pitch|transformers|torch'`).
