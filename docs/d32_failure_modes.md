# Day (d32) RGB failure-case taxonomy -- 2026-07-01

**Scope:** every GT instance + detection bucketed into {TP-correct, TP-wrong-class, FN, FP}; reconciled
to d26; broken down by object (raw class) / env / pose; FPs sub-bucketed. Self-contained on the d26
data (env-1 + env-2). Tier-2 lighting failures land in d35.
**Matching identical to d26 by construction:** `code/eval/failure_taxonomy.py` IMPORTS
`greedy_match_2d` / `canon` / `iou` / the loaders from `metrics.py` (untouched) and re-applies the same
conf filter (0.25) and IoU threshold (0.50) over non-occluded GT.
**Run:** `python3 code/eval/failure_taxonomy.py --gt docs/gt --runs code/eval/runs
--per-match docs/d26_metrics/per_match.csv --out docs/d32_failure
--fig docs/screenshots/d32_fig_failure_modes.png`

## Reconciliation (gate PASSED; equals the d26 presence table exactly)
- env1: assessable=12 TP=12 FN=0 FP=19 class_err=0 (TP-with-fused-range=12)
- env2: assessable=96 TP=29 FN=67 FP=16 class_err=5 (TP-with-fused-range=29)
- cross-check vs per_match.csv: fused rows there=41 vs TP-with-fused-range here=41 [OK]
- Miss breakdown reproduces the d26 known totals: bottle 11 + box 14 + trash bin 15 + chairs (6+15)=21
  + potted plant 6 = 67; class errors = box 3 + trash bin 2 = 5.

## Taxonomy by object (raw GT class)

| env | object | assessable | TP correct | TP wrong-class | FN | FN rate | med GT range FN (m) | med GT range TP (m) |
|---|---|---|---|---|---|---|---|---|
| env1 | chair | 3 | 3 | 0 | 0 | 0.00 | - | 1.36 |
| env1 | left monitor | 3 | 3 | 0 | 0 | 0.00 | - | 2.3 |
| env1 | person-in-chair | 3 | 3 | 0 | 0 | 0.00 | - | 4.22 |
| env1 | right monitor | 3 | 3 | 0 | 0 | 0.00 | - | 1.9 |
| env2 | bottle | 17 | 6 | 0 | 11 | 0.65 | 0.95 | 0.94 |
| env2 | box | 17 | 0 | 3 | 14 | 0.82 | 1.6 | 1.6 |
| env2 | chair1 | 17 | 11 | 0 | 6 | 0.35 | 1.75 | 1.42 |
| env2 | chair2 | 17 | 2 | 0 | 15 | 0.88 | 3.74 | 3.61 |
| env2 | potted plant | 11 | 5 | 0 | 6 | 0.55 | 7.38 | 7.74 |
| env2 | trash bin | 17 | 0 | 2 | 15 | 0.88 | 1.22 | 1.32 |

## Taxonomy by env / pose

| env | pose | assessable | TP correct | TP wrong-class | FN | recall |
|---|---|---|---|---|---|---|
| env1 | - | 12 | 12 | 0 | 0 | 1.000 |
| env2 | pose1 | 30 | 10 | 0 | 20 | 0.333 |
| env2 | pose2 | 30 | 6 | 2 | 22 | 0.267 |
| env2 | pose3 | 36 | 8 | 3 | 25 | 0.306 |

## Wrong-class matches (all 5, individually)

| env | pose | frame | GT class (raw) | predicted | conf | IoU |
|---|---|---|---|---|---|---|
| env2 | pose2 | 00400 | trash bin | potted plant | 0.458 | 0.859 |
| env2 | pose2 | 00600 | trash bin | potted plant | 0.333 | 0.927 |
| env2 | pose3 | 00100 | box | microwave | 0.252 | 0.949 |
| env2 | pose3 | 00200 | box | microwave | 0.252 | 0.935 |
| env2 | pose3 | 00400 | box | microwave | 0.267 | 0.943 |

## FP sub-buckets (totals equal the reconciliation FP counts)
- env1 (19): duplicate_detection 3 (chair x3, second box on the already-matched chair GT, IoU
  0.82-0.84, conf 0.39-0.62); no_gt_overlap 3 (laptop x2, keyboard x1); partial_overlap_below_iou 13
  (tv x9 at max-IoU 0.004-0.043 vs assessable, i.e. essentially zero overlap, + laptop x3, keyboard x1).
- env2 (16): no_gt_overlap 10 (remote x4, bottle x3, toilet x2, microwave x1);
  partial_overlap_below_iou 6 (potted plant x6, see finding F1).
- matches_occluded_gt: 0 everywhere (no detection landed on an occluded GT at IoU >= 0.50).

## Findings (measured fact first; interpretation flagged [interp])

**F1 -- the pose3 potted plant is a LOCALIZATION near-miss, not a detection failure (all 6 "misses").**
The plant splits by pose: pose1 (GT 7.74 m) matched correctly in 5/5 frames; pose3 (GT 7.38 m) is FN in
6/6 frames. But in ALL 6 pose3 frames a `potted plant` detection exists at conf 0.52-0.55 with IoU vs
the GT box of 0.396-0.481, just under the 0.50 gate, so each frame yields one FN AND one
partial-overlap FP. Measured IoUs: 0.449, 0.481, 0.396, 0.472, 0.415, 0.400 (at a 0.40 gate 5/6 would
match; at 0.45, 2/6). [interp] the detector sees and correctly names the plant every time; the box is
consistently looser than the annotation, plausibly the ~8 m tiny-object box-tightness limit. Headline
numbers stay at the frozen IoU 0.50; this is diagnostic only.
**F1b -- this also resolves the d26 section-3.2 "7.38 m" anecdote (decision-4 refinement).** 7.38 m is
the REAL GT tape range of the pose3 plant, whose overlay range read ~7.37 m; that object is FN under
the presence matching, so it never entered per_match.csv (whose matched plant is the pose1 7.74 m one).
The anecdote was a genuine observation on an object the matching then scores as a miss. Integration fix
options update: (a) keep the anecdote but label it precisely ("pose3 plant: class and range correct,
excluded from the matched set by the IoU gate at 0.40-0.48"), which is now the MOST informative option;
or (b) the previous soften/replace options. Victor picks at integration.

**F2 -- the far chair (chair2, ~3.6 m) lives at the confidence floor.** Only 2/17 matched, both pose3,
at conf 0.252 and 0.280, i.e. barely above the frozen 0.25 threshold; 15/17 FN. The near chair1
(~1.4-1.8 m) matches 11/17. [interp] range-driven confidence collapse on the same object class: the
miss mechanism is the detector's confidence falling through the floor with distance, not occlusion.

**F3 -- the bottle misses are NOT range- or threshold-driven.** Matched-bottle confs are 0.48-0.57
(well above the floor) and FN/TP median GT ranges are identical (0.95 vs 0.94 m). 6/17 matched.
[interp] frame-to-frame instability on a small object: the same bottle at the same range flickers in
and out of detection across frames.

**F4 -- the no-COCO-class objects are never correct, by construction, and fail in two ways.** box:
0/17 correct = 14 FN + 3 matched-as-microwave (conf 0.252-0.267, at the floor). trash bin: 0/17
correct = 15 FN + 2 matched-as-potted-plant (0.33, 0.46). [interp] out-of-vocabulary objects either
drop below confidence or get forced onto the visually nearest COCO class; the frozen alias map scores
them wrong either way, which is the honest accounting for a fixed-vocabulary detector.

**F5 -- pose is NOT the recall driver in env-2.** Recall per pose is flat: 0.333 / 0.267 / 0.306.
[interp] what an object is and how far it is dominates; viewpoint within this scene barely moves recall.

**F6 -- the env-1 precision story survives with more precision.** The 19 env-1 FPs are NOT
hallucinations: 3 are duplicate chair boxes on the matched chair; 16 are real-object detections with
zero-to-negligible GT overlap (tv x9 at IoU <= 0.043, laptop x5, keyboard x2), consistent with the d26
"out-of-annotation-scope" story (the d24 scope call deliberately left the desk laptop and far doorway
monitor unannotated). [interp] env-1 precision 0.387 measures annotation scope, not detector
hallucination; worth one sentence in the Discussion. Victor can eyeball the d14 canonical frames to
name the 9 tv detections (expected: the doorway/far monitors).

**F7 -- env-2's 10 out-of-scope FPs are the closest thing to hallucination.** remote x4, bottle x3,
toilet x2, microwave x1 with zero GT overlap. [interp] without looking at the frames these cannot be
attributed (clutter vs true hallucination); flag for a qualitative panel in d35 or a manual glance.

## Artifacts
- `code/eval/failure_taxonomy.py` (imports metrics.py; metrics.py untouched)
- `docs/d32_failure/{instances.csv, detections.csv, reconciliation.md, taxonomy_by_object.md,
  taxonomy_by_env_pose.md, class_errors.md, fp_analysis.md}`
- `docs/screenshots/d32_fig_failure_modes.png` (stacked per-object outcome bars, env-2 + FP sub-buckets)

## Done-criteria (d32)
- [x] failure_taxonomy.py reuses metrics.py and reproduces the d26 TP/FP/FN/class totals EXACTLY
      (gate passed first run; per_match cross-check 41=41).
- [x] Every env-2 miss (67) and class error (5) accounted for individually; env-1 fully reconciled.
- [x] Taxonomy tables + figure produced; FP sub-buckets sum to the FP totals.
- [x] Findings written (fact first, interpretation flagged). Subsection PROSE deferred to the writing
      chat per the standing decision; F1-F7 are the factual seed.
- [ ] VICTOR: eyeball the 9 env-1 tv FPs (expected doorway/far monitors) and the 10 env-2 out-of-scope
      FPs (F7) on the frames; pick the F1b anecdote fix at integration.
- [x] d32 manifest headline pasted into week06_log.md.
