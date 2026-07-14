# Architecture

Stemcell is a cached, staged pipeline plus two standalone generators. Everything is local and file-based.

## The stage model

Each stage is a module in `src/stemcell/` exposing exactly one function:

```python
def run(ctx: Ctx) -> None: ...
```

A stage reads whatever prior-stage outputs it needs from `ctx.outdir` and writes its own outputs there. Nothing is passed in memory between stages — so any stage can be skipped (cache hit), re-run in isolation, or resumed after a crash.

```
ingest → separate → analyze → drums → transcribe → report
```

| Stage | Reads | Writes | Engine |
|---|---|---|---|
| `ingest` | source audio | `input.wav` (44.1 kHz stereo) | ffprobe validate + ffmpeg |
| `separate` | `input.wav` | `stems/{drums,bass,other,vocals}.wav` | Demucs `htdemucs` (CPU, `--segment 5`) |
| `analyze` | stems | `analysis.json` (tempo, key, per-stem spectral tags) | librosa (beat_track, chroma_cqt, Krumhansl-Schmuckler) |
| `drums` | `stems/drums.wav`, `analysis.json` | `drums.json`, `oneshots/`, `loops/` | onset slice → MFCC dedupe → CLAP classify |
| `transcribe` | tonal stems, `analysis.json` | `midi/*.mid`, `midi/*.notes.json`, `manifest.json` | Spotify basic-pitch (CoreML) |
| `report` | all of the above | `report.json`, `report.md` | assembly |

## The `Ctx` contract

`ctx.py` defines `Ctx` (a dataclass of paths + lazily-loaded prior-stage JSON) and is the single source of truth for the output-directory layout. It also owns:

- **Caching** — `ctx.stage_done(name)` is a pure file-existence check per stage; `--force` bypasses it.
- **`seconds_to_beats()`** — the load-bearing conversion that turns basic-pitch's seconds-domain notes into the beats-domain note dicts Ableton's `add_notes_to_clip` expects.

## Crash safety

Stages write their JSON marker **last**, and `separate` renders into a temp dir that is renamed into `stems/` only on success — so an interrupted run never leaves a stage looking "done". Re-running resumes from the first incomplete stage.

## Standalone generators

Not part of the `run` pipeline; called directly (or by the `/dissect` skill):

- **`melody.py`** — `generate_hook_melody()` / `score_catchiness()`. Grounded hook-writing methodology (see [melody-methodology.md](melody-methodology.md)).
- **`vocalchop.py`** — `chop_vocal()` + MK/Todd pattern generators (`stemcell chop`). See [../references/house-vocal-chop-craft.md](../references/house-vocal-chop-craft.md).

## Knowledge bases

`references/*.md` are researched, fact-checked references consulted during orchestration — [`dance-gear-fingerprints.md`](../references/dance-gear-fingerprints.md) (identify a sound's likely gear source) and [`house-vocal-chop-craft.md`](../references/house-vocal-chop-craft.md) (MK/Todd technique + generator rules).
