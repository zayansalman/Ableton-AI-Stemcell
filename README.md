# song-dissect

Local audio dissection pipeline for music producers. Hand it a mixed song file and it
extracts, **from the audio itself** (not web lookups): separated stems, tempo/beatgrid,
key/scale, sliced + classified drum one-shots, beat-aligned drum loops, and polyphonic
MIDI transcription of the tonal parts. Outputs are shaped to feed a Splice text search
(`describe_a_sound`) and the `ableton-mcp` connector's `add_notes_to_clip`.

Runs entirely locally on Apple Silicon (built/tested on an M2, 8 GB RAM). No audio leaves
the machine.

## Install

```bash
cd ~/projects/song-dissect
uv sync
uv run song-dissect bootstrap   # one-time: downloads htdemucs (~80MB) + CLAP (~615MB)
```

`bootstrap` prints disk-free before/after and verifies ffmpeg is on PATH. The basic-pitch
CoreML transcription model ships with the wheel (no download).

## Use

```bash
uv run song-dissect run /path/to/song.mp3 --out ~/dissections/song
```

Stages run in order with file-existence caching — re-running skips completed stages
(`--force` re-runs all, `--stages analyze,drums` runs a subset). On an M2, Demucs
separation dominates (~3–8 min for a 4-min track, CPU); everything else is ~1–2 min.

```bash
uv run song-dissect selftest    # offline synthetic check, no models, no copyrighted audio
```

## Output contract

```
<outdir>/
  input.wav                      normalized 44.1kHz stereo source
  stems/{drums,bass,other,vocals}.wav
  oneshots/<label>_NN.wav        label ∈ kick,snare,clap,hat_closed,hat_open,crash,ride,
                                 tom,shaker,tamb,rim,snap,cowbell,perc  (CLAP-classified)
  loops/drums_bars_AAA-BBB.wav   beat-aligned drum loops
  midi/<stem>.mid                bass/other/vocals (unless silent)
  midi/<stem>.notes.json         add_notes_to_clip-ready: {pitch,start_time,duration,velocity,mute}, beats
  report.json                    authoritative machine-readable output (schema_version 1)
  report.md                      human-readable summary
```

`report.json` carries tempo (with half/double candidates + stability), key (with
relative/parallel alternates + confidence), per-stem spectral tags + ready-made Splice
query hints, the drum-hit inventory, and per-stem MIDI stats. All internal paths are
relative to `<outdir>`.

## Modules

| Module | Responsibility |
|---|---|
| `ingest.py` | ffprobe validation + ffmpeg normalize → `input.wav` |
| `separate.py` | Demucs `htdemucs` → 4 stems (crash-safe temp-dir rename) |
| `analyze.py` | tempo/beatgrid, Krumhansl-Schmuckler key, per-stem loudness/spectral tags |
| `drums.py` | onset slice → MFCC dedupe → CLAP classify → one-shots + loops |
| `transcribe.py` | basic-pitch audio→MIDI, seconds→beats for `add_notes_to_clip` |
| `report.py` | merge → `report.json` + `report.md` |
| `melody.py` | catchy-hook methodology + `generate_hook_melody()` / `score_catchiness()` |

### `melody.py`

Standalone (numpy-only, no audio stack). Turns music-cognition research — Huron's ITPRA
expectation theory, Jakubowski's earworm-contour findings, motif economy /
repetition-with-variation, antecedent-consequent phrasing, strong-beat anchoring — into
`generate_hook_melody(root_pitch, scale, tempo_bpm, bars)` (returns notes ready for
`add_notes_to_clip`) and `score_catchiness(notes, tempo_bpm)` (five 0..1 sub-scores +
overall; infers the melody's key when not supplied).

## Limitations (v1)

Constant-tempo assumption (report's `tempo_stability` is the honesty signal); 4/4 assumed
for loop slicing; CLAP gear-ID (808 vs 909) is hint-grade, not authoritative; no
synth-parameter reverse-engineering; no lyrics/section detection. Sliced hits from
commercial recordings are for reference and learning — use the Splice-matched licensed
equivalents in released music.
