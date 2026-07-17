# Day (d31) literature comparison + positioning -- 2026-07-01

**Scope:** accuracy-vs-efficiency comparison of the training-free frustum method against three published
LiDAR-camera fusion methods (PointPainting, BEVFusion/Liang, DeepInteraction++), on the axis the
supervisor asked for in review: how far the method is on accuracy, net of the computational-efficiency
trade-off that the fusion literature usually does not weigh.
**This is a CONCEPTUAL + QUANTITATIVE comparison, NOT an empirical run.** An empirical out-of-distribution
run of these methods is scoped as future work / optional stretch (see the last section).
**Sources:** the three method PDFs; `bevsurvey2026` (IEEE T-ITS survey, Table V); `bevcmhf2026` (Table I);
the DeepInteraction++ PDF (`deepinteraction2025`). Numbers are flagged inline where single-source or not
legible from a scan. Per the accuracy rules, nothing unverified is stated as fact.

## Framing rules (locked with the supervisor's comments and the existing thesis text)
- The nuScenes mAP/NDS figures below are IN-DOMAIN road-benchmark results for the three published methods.
  They are NOT comparable to this work's out-of-distribution indoor presence recall: different metric
  (mAP/NDS vs presence recall), different data (road vs indoor), and a deliberately harder domain. They
  are shown only as context for the efficiency trade-off. This mirrors how `sec:disc-domaingap` already
  treats the T-3MS 71.51 -> 79.76 numbers (directional only, explicitly not a head-to-head).
- Consistency: DeepInteraction is represented by the ++ version (`deepinteraction2025`), the SAME entry
  already cited in Related Work. The 2022 original is NOT added, to avoid two entries a reader must
  reconcile. (Caveat carried forward: any specific number used for this row must come from the ++ paper,
  not the 2022 original; see the accuracy flags.)

## Comparison table

| Method | Fusion type / level | Training required | Reported nuScenes accuracy (IN-DOMAIN; NOT comparable to this work) | Compute / hardware class | Real-time on embedded? | Eval domain |
|---|---|---|---|---|---|---|
| PointPainting | input-level / sequential: decorate LiDAR points with 2D image segmentation scores, then a trained LiDAR detector | Yes (segmentation net + LiDAR detector) | test approx. 46.4 mAP / 58.1 NDS [survey Tab. V only among my sources; verify] | GPU-class (seg + detector); specific latency not verified here | Not designed for it | nuScenes, KITTI (road) |
| BEVFusion (Liang et al., NeurIPS 2022) | feature-level, unified BEV; two independent streams (LSS camera BEV + LiDAR BEV) + dynamic fusion | Yes | val approx. 67.9 / 71.0, test approx. 69.2 / 71.8 [survey Tab. V + BEV-CMHF Tab. I (val); verify] | GPU-class; specific latency not verified here | Not designed for it | nuScenes (road) |
| DeepInteraction++ (2025, `deepinteraction2025`) | modality INTERACTION: two modality-specific reps maintained throughout; dual-stream Transformer encoder + predictive-interaction decoder | Yes (9 epochs on 8x A6000, Swin-Tiny image backbone) | new nuScenes SOTA claimed; approx. 70.6 mAP / 73.3 NDS on val per the paper's OWN ablation (Tab. VIII) -- read the exact HEADLINE from Tab. I (not legible in my scan) | server GPU (RTX A6000 in the paper); assumes 6 surround cameras | No (server-class) | nuScenes (road) |
| This work (frustum fusion) | late / frustum: 2D detection -> frustum -> DBSCAN range; detect-then-locate (DAL-style) | NO (training-free: pretrained COCO YOLOv8 + pretrained nuScenes PointPillars, zero-shot, no fine-tuning) | N/A on nuScenes (not benchmarked). OOD indoor presence recall 1.0 (env-1) / 0.30 (env-2), a different metric on a harder domain | embedded (Jetson Orin NX / ZED Box) | Yes, approx. 8 Hz | indoor, out-of-distribution (this thesis) |

## Per-method grounding (verifiable characterizations)
- **PointPainting** -- "the pioneering input fusion method" that decorates the 3D point cloud with
  category scores / semantic features from a 2D instance-segmentation network, then runs a LiDAR
  detector on the painted cloud (described in DeepInteraction++ Sec. II and in the PointPainting paper).
  It is the method the supervisor flagged as conceptually closest to this work: both route image
  semantics onto LiDAR points. Difference: this work attaches a RANGE via a 2D-box frustum + DBSCAN and
  uses pretrained detectors with NO painting-specific training, whereas PointPainting needs both a
  trained segmentation network and a detector trained on the painted representation.
- **BEVFusion (Liang)** -- converts each modality independently into a shared BEV feature map (camera via
  Lift-Splat-Shoot, LiDAR via a 3D backbone) and fuses them; the camera stream does not depend on LiDAR
  input, which the paper frames as robustness. Feature-level parallel fusion. Trained end-to-end on
  nuScenes.
- **DeepInteraction++** -- rejects merging into a single fused tensor; maintains two modality-specific
  representations throughout, exchanging information via a dual-stream Transformer (representational
  interaction) and a predictive-interaction decoder, with LiDAR-guided cross-plane polar ray attention
  and grouped sparse attention. Trained on nuScenes (9 epochs, 8x A6000). Extended to end-to-end driving.
  Runtime measured on a single RTX A6000 (server GPU).
- **This work** -- late/frustum, detect-then-locate: the camera (YOLOv8, COCO) classifies, the LiDAR
  (PointPillars, nuScenes) localises, fused by frustum + DBSCAN. Training-free and zero-shot; deployed on
  a Jetson Orin NX at approx. 8 Hz; evaluated out of distribution indoors. All four facts are verifiable
  from Chapters ref{ch:methodology} and ref{ch:results}.

## Domain-gap grounding (link to the thesis's existing evidence)
- All three reference methods are trained AND evaluated on road data (nuScenes / KITTI). This work's
  contribution is a different operating point: training-free, embedded, real-time, and characterised OUT
  of the training distribution.
- The thesis already supplies the out-of-distribution evidence for a road-trained detector: the
  LiDAR-only PointPillars baseline produced ZERO detections above 0.30 on all 17 env-2 frames
  (`sec:disc-domaingap`), the cleanest single number in the work. An empirical OOD run of PointPainting /
  BEVFusion / DeepInteraction++ shares that road-trained-detector premise and would be EXPECTED to
  reproduce the same domain gap, which is exactly why an empirical comparison is scoped as future work
  rather than presented as a head-to-head result here.
- Accuracy-axis caveat (restated for the table): the nuScenes mAP/NDS above are in-domain road-benchmark
  numbers; they are not comparable to this work's OOD indoor presence recall. This is the same discipline
  the thesis already applies to the T-3MS numbers.

## Accuracy numbers -- sourcing + verification flags (per the accuracy rules)
- **PointPainting pages DISCREPANCY:** `4604--4612` (survey ref [153] + BEV-CMHF ref [17]) vs `4603--4611`
  (DeepInteraction++ ref [1]). One-page difference; I cannot resolve it from here. VERIFY against the
  CVPR 2020 proceedings / the PointPainting PDF before final submission.
- **PointPainting nuScenes 46.4 / 58.1 (test):** appears in `bevsurvey2026` Table V only among my sources
  (val is blank there). Not independently cross-checked. VERIFY against the PointPainting paper's own
  table.
- **BEVFusion (Liang) arXiv 2205.13790:** triple-confirmed (survey [159], BEV-CMHF [21], DeepInteraction++
  [9]). NeurIPS 2022 pages `10421--10434`: survey + BEV-CMHF (consistent). Full 9-author list: NOT verified
  from the primary PDF (all three secondary sources abbreviate "T. Liang et al."); VERIFY the full list
  and order against the BEVFusion PDF you hold.
- **BEVFusion (Liang) nuScenes:** val 67.9 / 71.0 is cross-confirmed (survey Tab. V + BEV-CMHF Tab. I);
  test 69.2 / 71.8 is from survey Tab. V only. Treat as approximate; verify against the BEVFusion paper.
- **DeepInteraction++ headline nuScenes mAP/NDS:** the main results table (Table I, test set) is NOT
  legible in the scan I have. The approx. 70.6 / 73.3 in the table above is from Table VIII (a val
  decoder-design ablation) and may NOT be the headline configuration. READ the exact headline test-set
  mAP/NDS off Table I of your DeepInteraction++ PDF and replace the placeholder.
- **DeepInteraction++ authors + page range:** authors (Yang, Song, Li, Zhu, Zhang, Torr) confirmed from
  the PDF first page. The page range `6749--6763` in your existing `deepinteraction2025` entry (flagged
  "verify" in your bib header) is now CONFIRMED from the PDF (bios end on p. 6763); that flag can be
  cleared.

## references.bib -- add 2 entries; reuse the existing `deepinteraction2025` for DeepInteraction

```bibtex
@inproceedings{pointpainting2020,
  author    = {Vora, Sourabh and Lang, Alex H. and Helou, Bassam and Beijbom, Oscar},
  title     = {{PointPainting}: Sequential Fusion for {3D} Object Detection},
  booktitle = {IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
  pages     = {4604--4612},  % survey + BEV-CMHF; DeepInteraction++ ref lists 4603--4611 -- VERIFY
  year      = {2020}
}

@inproceedings{bevfusion2022,
  author    = {Liang, Tingting and Xie, Hongwei and Yu, Kaicheng and Xia, Zhongyu and Lin, Zhiwei and Wang, Yongtao and Tang, Tao and Wang, Bing and Tang, Zhi},  % full list from earlier read; sources abbreviate "et al." -- VERIFY against the PDF
  title     = {{BEVFusion}: A Simple and Robust {LiDAR}-Camera Fusion Framework},
  booktitle = {Advances in Neural Information Processing Systems (NeurIPS)},
  pages     = {10421--10434},
  year      = {2022}
  % arXiv:2205.13790 (triple-confirmed). NOT the MIT BEVFusion (Liu et al., ICRA 2023, arXiv:2205.13542).
}
```

Do NOT add a `deepinteraction2022` entry: the DeepInteraction row uses the existing `deepinteraction2025`
(++), per the consistency decision.

## Positioning seed (factual only; prose is deferred to the writing chat)
- This work is not an accuracy competitor to the three methods; it targets the efficiency / deployment /
  OOD operating point they do not address. Foreground three verifiable contrasts: training-free (vs all
  three trained on nuScenes), embedded real-time on a Jetson Orin NX at approx. 8 Hz (vs server/desktop
  GPU), and evaluated out of distribution indoors (vs in-domain road benchmarks).
- The three exemplify the trained / in-domain / accuracy-focused SOTA at three fusion levels: input
  (PointPainting), BEV feature (BEVFusion), and interaction (DeepInteraction++). PointPainting is the
  conceptual neighbour; the other two mark where the accuracy-focused line has gone.
- The existing `sec:rw-positioning` and `sec:disc-domaingap` already carry the positioning; this manifest
  supplies the comparison content those sections currently lack (explicit method table + the efficiency
  axis), not a replacement for them.

## Empirical run (future work / optional stretch)
- Rationale for deferring: all three are road-trained; an OOD indoor run is expected to reproduce the
  domain gap the LiDAR-only baseline already demonstrates (env-2 zero above 0.30). PointPainting is the
  only one the supervisor judged "not hard to adapt", but a faithful run still needs a 2D
  segmentation network plus a detector trained on the painted representation, both road-domain, so the
  painted semantics would not correspond to indoor objects; retraining would break the training-free
  premise. Expected outcome: "we ran the closest published method and, like the LiDAR-only baseline, it
  fails OOD indoors" -- a real but largely predictable confirmation.
- If attempted with spare days after Priority 1 (Tier 2 + failure taxonomy), it belongs as an optional
  appendix result, framed exactly as above.

## Done-criteria (d31)
- [x] Existing Related Work + Discussion read; overlaps identified (positioning already exists in
      `sec:rw-positioning`; T-3MS is the anchor; PointPainting described but uncited; BEVFusion named via
      T-3MS but uncited; DeepInteraction cited only as ++).
- [x] Comparison table built (4 methods x 7 axes); accuracy labelled in-domain and not comparable.
- [x] Method characterizations grounded + sourced; all uncertain numbers flagged.
- [x] 2 new bib entries drafted (`pointpainting2020`, `bevfusion2022`); DeepInteraction reuses
      `deepinteraction2025`.
- [ ] VICTOR to verify the flagged items against the primary PDFs: PointPainting pages (4603-4611 vs
      4604-4612) and its 46.4/58.1; BEVFusion 9-author list; DeepInteraction++ headline mAP/NDS from
      Table I.
- [ ] (Deferred to the writing chat) turn the table + positioning seed into thesis prose / a LaTeX table.
