# Ableton-AI-Stemcell 🧬

**Reverse-engineer any track and regrow it in Ableton.** Hand Stemcell a song and it dissects the audio itself — stems, tempo, key, drum one-shots, MIDI of every part — identifies the *gear* behind each sound, finds licensed look-alikes on Splice, generates catchy melodies and MK/Todd-Edwards-style vocal chops, and rebuilds the whole thing into a live Ableton project.

It runs **entirely locally** (built and tested on Apple Silicon, M2 / 8 GB). No audio ever leaves your machine.

> **Not affiliated with, endorsed by, or sponsored by Ableton AG or Splice.com.** "Ableton", "Live", "Simpler" and "Splice" are trademarks of their respective owners. This is an independent, open-source hobby project that *integrates with* those tools.

---

## What it does

| Capability | How |
|---|---|
| 🎚️ **Dissect** | Demucs stem separation · librosa tempo/beatgrid + Krumhansl-Schmuckler key · onset-sliced drum one-shots · Spotify basic-pitch → MIDI (in beats) |
| 🥁 **Identify the gear** | CLAP zero-shot + spectral fingerprints, mapped through a researched knowledge base (TR-909/808, Korg M1, Juno, …) to a probable source *with an honest confidence tier* |
| 🎹 **Generate catchy melodies** | A grounded hook generator (Huron ITPRA, Jakubowski earworm contour, motif economy) → MIDI ready for Ableton |
| 🎤 **Vocal chops** | Chop a vocal → **MK-style** pitched offbeat stabs (Simpler Classic) and **Todd-Edwards-style** swung slice mosaics (Simpler Slice), matched to the track's scale/tempo |
| 🔎 **Source on Splice** | Turns measured features + gear ID into text searches for licensed, royalty-free equivalents |
| 🎛️ **Rebuild in Ableton** | Drives a live Ableton session via the `ableton-mcp` connector — sets tempo, makes tracks, writes the MIDI, imports samples |

## Architecture

```mermaid
flowchart LR
    A[audio file] --> B[ingest<br/>ffmpeg normalize]
    B --> C[separate<br/>Demucs htdemucs]
    C --> D[analyze<br/>tempo · key · spectral]
    C --> E[drums<br/>slice · CLAP · loops]
    C --> F[transcribe<br/>basic-pitch → MIDI]
    D --> G[report.json + report.md]
    E --> G
    F --> G
    G --> H{orchestration}
    H -->|gear ID| I[dance-gear-fingerprints KB]
    H -->|queries| J[Splice MCP]
    H -->|rebuild| K[ableton-mcp → Live]
    L[vocal sample] --> M[chop<br/>MK + Todd MIDI] --> K
```

The pipeline writes a machine-readable `report.json` (schema v1); everything downstream is driven by measured values, never by re-listening. See [`docs/output-schema.md`](docs/output-schema.md).

## Requirements

- **macOS Apple Silicon** (CPU inference; built on M2 / 8 GB / Python 3.11). Other platforms likely work but are unverified — the lockfile is pinned to `darwin/arm64`.
- [`uv`](https://github.com/astral-sh/uv), `ffmpeg`, and ~2 GB free disk for the models.
- **Optional integrations:** the [`ahujasid/ableton-mcp`](https://github.com/ahujasid/ableton-mcp) connector (to rebuild in Live) and a Splice MCP connector (to source samples). Stemcell works standalone without them — you just get the analysis + files.

## Install

```bash
git clone https://github.com/zayansalman/Ableton-AI-Stemcell.git
cd Ableton-AI-Stemcell
uv sync
uv run stemcell bootstrap   # one-time: downloads htdemucs (~80 MB) + CLAP (~615 MB); prints disk-free
```

The basic-pitch CoreML model ships with the wheel (no download). To rebuild in Ableton, also install the [ableton-mcp connector](https://github.com/ahujasid/ableton-mcp) — see [`docs/ableton-integration.md`](docs/ableton-integration.md).

## Quickstart

```bash
# Dissect a track
uv run stemcell run /path/to/song.mp3 --out ~/dissections/song
cat ~/dissections/song/report.md

# Chop a short (1–2 bar) vocal phrase into a playable kit + MK/Todd patterns
uv run stemcell chop /path/to/vocal.wav --out ~/chops/vox --tempo 123 --root C --scale minor

# Offline self-check (no models, no copyrighted audio)
uv run stemcell selftest
```

Stages cache by file-existence — re-running skips completed stages (`--force` to redo, `--stages analyze,drums` for a subset). Demucs is the slow stage (~2 min per audio-minute on M2 CPU).

## Output contract

```
<outdir>/
  input.wav                      normalized 44.1 kHz stereo source
  stems/{drums,bass,other,vocals}.wav
  oneshots/<label>_NN.wav        CLAP-classified: kick, snare, hat_open, clap, …
  loops/drums_bars_AAA-BBB.wav   beat-aligned drum loops
  midi/<stem>.mid + .notes.json  transcribed parts, notes in BEATS (add_notes_to_clip-ready)
  report.json                    authoritative machine-readable output (schema v1)
  report.md                      human-readable summary
```

## Use with Claude Code

Stemcell is designed to be driven by an AI agent. The bundled `/dissect` skill ([`integrations/claude-skill/`](integrations/claude-skill/)) teaches [Claude Code](https://claude.com/claude-code) to run the pipeline, read `report.json`, identify gear, build Splice queries, and rebuild in Ableton — end to end from a single prompt.

## Honest limitations

- Constant-tempo and 4/4 are assumed; `report.tempo.tempo_stability` is the honesty signal for rubato.
- **Gear ID is inference, not proof.** CLAP's "909" axis is really a "punchy/has-a-click" flag; the knowledge base is explicit about documented-vs-lore.
- Full-mix stem transcription (esp. the `other` stem) is a harmonic *sketch*, not clean MIDI. The bass stem transcribes best.
- The Live scripting API can't load a sample into a playable Simpler — vocal chops need **one manual drag** (documented in the emitted `README.txt`).
- No synth-preset reverse-engineering; sliced hits from commercial recordings are for **reference/learning** — use the Splice-matched licensed equivalents in released music.

## Credits & Licenses

Stemcell is **MIT-licensed** (see [`LICENSE`](LICENSE)). It stands on excellent open-source work, all downloaded at runtime (not redistributed here) — see [`NOTICE`](NOTICE):

| Project | Role | License |
|---|---|---|
| [Demucs](https://github.com/facebookresearch/demucs) (Meta) | stem separation + htdemucs weights | MIT |
| [basic-pitch](https://github.com/spotify/basic-pitch) (Spotify) | audio → MIDI | Apache-2.0 |
| [CLAP](https://huggingface.co/laion/clap-htsat-unfused) (LAION) | zero-shot audio classification | Apache-2.0 |
| [librosa](https://librosa.org) | tempo / key / onsets | ISC |
| [transformers](https://github.com/huggingface/transformers), [PyTorch](https://pytorch.org) | model runtime | Apache-2.0 |
| [ableton-mcp](https://github.com/ahujasid/ableton-mcp) (optional) | Live control | MIT |

Contributions welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md). Full guides in the [Wiki](../../wiki) and [`docs/`](docs/).
