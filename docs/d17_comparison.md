# Day 4 (d17) fused-vs-baseline manifest -- 2026-06-04

**Baseline anchor:** Day-6 LiDAR-only PointPillars-MultiHead on the same frames (see `d13_pointpillars_manifest.md`).
**Fused source:** Day-3 frustum fusion, `code/fusion/fused_out/{00100,00300,00500}.json` (see `d16_fusion.md`).
Both report position in the LiDAR frame, so ranges are directly comparable (range = hypot(x, y)).

## Day-6 LiDAR-only detections (headless run, score >= 0.30)
- 00100: trailer 0.94 m (s0.37); pedestrian 5.30 m (s0.36); pedestrian 5.27 m (s0.34). [No 4.3 m above threshold; GUI re-run caught ~4.45 m -- score jitter.]
- 00300: trailer 1.29 m (s0.43); pedestrian 4.33 m (s0.37); pedestrian 5.29 m (s0.32).
- 00500: truck 0.97 m (s0.52); pedestrian 5.25 m (s0.34); + pedestrians 4.34 / 5.33 m and a 2nd near-field trailer (GUI/threshold jitter).

## Fused detections (Week 3, condensed; full JSON in code/fusion/fused_out/)
- 00100 (11): chair 1.76 m; tv 2.35/2.01/2.62 m; chair 4.46 m + person 4.46 m (doorway); laptop 2.69 m; tv+laptop 5.29 m (far); keyboard 2.30 m; tv 8.06 m.
- 00300 (10): chair 1.76 m; tv 2.35/2.01/2.62 m; person 4.31 m + chair 4.31 m (doorway); laptop 2.68 m; tv 5.29 m; tv 8.06 m; laptop 5.29 m.
- 00500 (10): chair 1.76 m; tv 2.35/2.01/2.62 m; tv 5.29 m; chair 4.31 m; keyboard 2.31 m; laptop 2.67 m; tv 8.06 m; person 4.31 m.
- All boxes fused (no camera-only fallback). Nearest fused object is the tan chair at 1.76 m; nothing fused in the ~1 m near field.

## Fused vs LiDAR-only (per region/object, same frames 00100/00300/00500)
| Region / object | LiDAR-only (Day-6, score>=0.30) | Fused (Week 3) | Outcome |
|---|---|---|---|
| Near-field ~1 m | trailer/truck every frame (00100 0.94m s0.37; 00300 1.29m s0.43; 00500 0.97m s0.52) | no detection (no camera box) | SUPPRESSED in all 3 frames -- headline fusion win |
| Person-in-blue-chair ~4 m (GT 4.00 m) | pedestrian @4.33m (00300 s0.37; 00500 s0.33); borderline/below threshold in 00100 headless | chair/person @4.31-4.46m, all 3 frames | range matches (4.31 vs 4.33 m); camera adds class; fusion detects in all 3 frames (LiDAR-only intermittent); person-in-chair, class genuinely ambiguous |
| Far-room ~5.3-8 m (through doorway/glass) | pedestrian(s) @5.25-5.33m every frame (s0.30-0.36) | tv/laptop @5.29m and 8.06m (matching range) | camera reclassifies far-room monitors/desk; Day-6 pedestrian@5.3m is itself a likely misclassification; per-object pairing approximate in clutter |
| Tan high-back chair (no GT marker) | not detected | chair @1.76m (s0.94) | fusion detects a real chair LiDAR-only missed (camera-driven) |
| 100 cm black chair @1.0 m | missed (inside hallucination footprint) | no detection (no camera box / not in monocular view) | missed by both modalities |
| doorway @1.8 m | correctly none | correctly none | n/a |

## Blue-chair correspondence
- Overlay `docs/screenshots/d17_bluechair_overlay.png`: the ~4.33 m highlight band (magenta) projects onto the doorway person-in-chair. The Day-6 `pedestrian @4.33 m` and the fused `chair/person @4.31 m` are the same physical object.
- Camera class on that object: chair (00100/00500) / person (00300), overlapping boxes -- per-frame flip.
- Status: person-in-chair confirmed (Victor); fused range matches Day-6 to a few cm. This is a single confirmed correspondence, NOT a calibrated range-accuracy figure. The +0.33 m (4.33 vs GT 4.00) stays a marker-vs-detection offset, anecdotal.

## Figures
- `docs/screenshots/d17_fused_vs_baseline.png` -- before/after (Day-6 PointPillars boxes vs Week-3 scene). NOTE: built with the projection overlay (d15) on the right; for a true fused-vs-baseline panel regenerate with the fused viz `d16_clusters_00300.png` using `code/fusion/make_figure.py`.
- `docs/screenshots/d17_bluechair_overlay.png` -- ~4.33 m band highlighted on the person-in-chair.

## Final state
- Near-field trailer/truck hallucination suppressed: YES, all 3 frames (no camera box -> no fused detection). Headline win.
- Person-in-blue-chair ~4 m: fused chair/person @4.31-4.46 m; range matches Day-6 4.33 m. NOT a clean chair->pedestrian fix (person-in-chair, both labels partly right); class camera-dependent per frame.
- Tan chair: recovered by fusion @1.76 m (LiDAR-only missed it).
- Far-room ~5.3 m: camera reclassifies as tv/laptop; Day-6 pedestrian@5.3 m is itself a likely misclassification of far-room monitors.
- 100 cm black chair @1 m: still missed by both modalities.
- Blue-chair status: person-in-chair confirmed; range matches Day-6; NOT a calibrated range figure.
- Day 4 outcome: PASS.
