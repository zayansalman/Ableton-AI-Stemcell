# Ableton integration

Stemcell rebuilds tracks in a **live** Ableton Live session through the third-party [`ableton-mcp`](https://github.com/ahujasid/ableton-mcp) connector (MIT). This is real Live Object Model control over a socket — **not** screen automation.

## One-time setup

1. Install the connector and copy its Remote Script into `~/Music/Ableton/User Library/Remote Scripts/AbletonMCP/` (see the ableton-mcp README).
2. In Live → **Settings → Link, Tempo & MIDI**, set a **Control Surface** slot to `AbletonMCP` (Input/Output = None).
3. Register the MCP server with your agent (e.g. `claude mcp add ableton-mcp -- uvx ableton-mcp`).

Verify with `get_session_info` — it returns the open set's tempo/tracks if connected.

## Tools used to rebuild

`set_tempo` · `create_midi_track` / `set_track_name` · `create_clip` + `add_notes_to_clip` (pass a `notes.json` array verbatim) · `create_audio_clip` (import a stem/loop/one-shot) · `load_instrument_or_effect` (by browser URI) · `get_browser_tree`.

**Safety:** these mutate whatever set is currently open. Confirm before writing into a real project; prefer a blank set.

## What the connector CANNOT do (by design of the Live API)

- **Set device parameters** (EQ/synth knob values) — load a device, but dial it in by hand.
- **Reach inside a Drum Rack pad chain** — devices load at the track level only.
- **Load a sample into a Simpler/Sampler** — the Live scripting API has no such call. This is why vocal chops need one manual drag (below).
- **Load third-party VST presets** (e.g. a specific Serum patch) — source the sound as audio from Splice instead.

## Vocal chops — the one manual drag

`stemcell chop` produces `slices/`, `mk.notes.json`, `todd.notes.json`, and a `README.txt`. Because the API can't load a sample into a Simpler, you do one ~10-second step; the agent does the rest.

**MK mode (pitched stabs):**
1. Drag the one chop named in `mk.notes.json`'s `load_slice` onto a MIDI track → Simpler.
2. Leave Simpler in **Classic** mode; set Transpose so the chop sounds at the root.
3. Agent loads `mk.notes.json` via `add_notes_to_clip` — the notes are real pitches following the progression; Classic mode transposes the chop to each.

**Todd mode (rhythmic mosaic):**
1. Drag the whole vocal onto a MIDI track → Simpler → set playback to **Slice** mode.
2. Simpler maps slice 0 → C1 (MIDI 36), slice 1 → C#1 (37)… chromatically.
3. Agent loads `todd.notes.json` — its notes trigger slices in a swung 16th mosaic.

## Fully-automating the chop load (future)

Getting a sample into a slice-mode Simpler with zero manual steps would need either the browser **hotswap** API from within an extended Remote Script, or a small **Max for Live** device that receives a path and loads it. Both are real work with uncertain feasibility — tracked as a possible future extension, not shipped.
