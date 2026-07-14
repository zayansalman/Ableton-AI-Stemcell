# Output schema (`report.json`, schema_version 1)

The authoritative machine-readable output. All internal paths are relative to `<outdir>`.

```jsonc
{
  "schema_version": 1,
  "generated_at": "<ISO8601 UTC>",
  "source": { "path": str, "duration_sec": float, "sample_rate": int, "channels": int },

  "tempo": {
    "bpm": float,
    "confidence": float,                 // == tempo_stability, 0..1
    "candidates": [ { "bpm": float, "relation": "primary"|"half"|"double" } ],
    "grid_offset_sec": float,
    "beat_count": int,
    "tempo_stability": float,            // low (<0.7) => rubato/variable-tempo warning
    "assumed_meter": "4/4"
  },

  "key": {
    "tonic": str,                        // "C", "F#" (sharps)
    "mode": "major"|"minor",
    "name": str,                         // "C minor"
    "confidence": float,                 // margin between best and 2nd-best; low => ambiguous
    "alternates": [ { "name": str, "relation": "relative"|"parallel", "score": float } ],
    "chroma_profile": [float; 12]        // C..B, normalized
  },

  "stems": {                             // one per drums|bass|other|vocals
    "<stem>": {
      "path": str,
      "rms_db": float, "peak_db": float,
      "activity_ratio": float, "silent": bool,
      "spectral": { "centroid_hz": float, "rolloff_hz": float, "flatness": float, "lowband_ratio": float },
      "tags": [str],                     // "bright","warm/dark","sub-heavy","punchy","noisy/textured"
      "splice_query_hints": [str]        // ready-made Splice searches
    }
  },

  "drums": {
    "onset_count": int, "unique_hits": int,
    "oneshots": [ {
      "file": str,                       // "oneshots/kick_01.wav"
      "label": str,                      // kick|snare|clap|hat_closed|hat_open|crash|ride|tom|shaker|tamb|rim|snap|cowbell|perc
      "clap_confidence": float,
      "alt_labels": [ { "label": str, "confidence": float } ],
      "character_hints": [ { "label": str, "confidence": float } ],   // "909 drum machine" etc. — HINT-GRADE
      "source_time_sec": float, "duration_sec": float,
      "count_in_song": int, "peak_db": float,
      "spectral": { ... }, "tags": [str], "splice_query_hints": [str]
    } ],
    "loops": [ { "file": str, "start_bar": int, "num_bars": int, "start_sec": float, "duration_sec": float, "rms_db": float } ]
  },

  "midi": {                              // one per bass|other|vocals
    "<stem>": {
      "skipped": bool, "skip_reason": str|null,
      "midi_file": str|null, "notes_file": str|null,
      "note_count": int, "pitch_range": [int, int],
      "median_velocity": int, "clip_length_beats": float,
      "beat_alignment_score": float      // fraction of notes near the 16th grid
    }
  },

  "warnings": [str]
}
```

## `notes.json` (per tonal stem, and from `stemcell chop`)

The `notes` array is usable **verbatim** as the `notes` argument to the `ableton-mcp` connector's `add_notes_to_clip(track, clip, notes)`:

```jsonc
{
  "stem": str, "tempo_bpm": float, "grid_offset_sec": float,
  "clip_length_beats": float, "note_count": int,
  "notes": [ { "pitch": int, "start_time": float, "duration": float, "velocity": int, "mute": false } ]
                          //          ^ beats            ^ beats
}
```

Chop kits add `mode` (`mk`|`todd`), `simpler_mode` (`Classic`|`Slice`), and (MK) `load_slice` — see [ableton-integration.md](ableton-integration.md).
