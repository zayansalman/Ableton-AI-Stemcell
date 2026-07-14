# Melody methodology

`stemcell.melody` turns music-cognition research into two usable tools. The full grounded methodology (with sources) lives in the module docstring; this is the summary.

```python
from stemcell.melody import generate_hook_melody, score_catchiness

notes = generate_hook_melody(root_pitch=60, scale="minor", tempo_bpm=123, bars=4)
# -> notes[] in the add_notes_to_clip schema (beats domain)

score_catchiness(notes, 123)   # 5 sub-scores + overall; infers the key if you don't pass it
```

## The principles it encodes

- **Huron's ITPRA** (*Sweet Anticipation*) — catchiness lives in the narrow band between fully predictable (boring) and fully unpredictable (won't stick): set an expectation, then confirm or gently violate it.
- **Statistical / schema expectation** — "prototypicality with a twist" beats both generic and fully-novel.
- **Jakubowski's "Dissecting an earworm"** — mostly stepwise (conjunct) motion punctuated by a few salient leaps; compact contour.
- **Motif economy + repetition-with-variation** — one short cell reused (transposed/sequenced), the single highest-leverage memorability move.
- **Antecedent–consequent phrasing** — a 2-bar question answered by a 2-bar response that resolves harder to the tonic.
- **Strong-beat anchoring** — hooks lock to beats 1 & 3 with 1–2 syncopated "hook points", not constant syncopation.
- **Resolution** — final phrase lands on scale degree 1 or 3 for closure.

## `score_catchiness` sub-scores (each 0..1)

`range_compactness` · `stepwise_ratio` (peaks at 60–85% stepwise, not 100%) · `motif_repetition` · `beat_anchoring` · `resolution` → unweighted `overall`. Pass `root_pitch`/`scale` for an exact resolution read, or let it infer the key from the melody's own pitch-class distribution.

Use it to fill an empty arrangement section, or to sanity-check a generated line before dropping it into Live.
