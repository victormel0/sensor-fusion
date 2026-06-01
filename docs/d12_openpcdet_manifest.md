# Day 5 OpenPCDet install manifest -- 2026-05-27

**Calibration branch chosen (from §5.1):** good - calibration accepted on Day 4 (see `d11_calibration_manifest.md`); proceeded to OpenPCDet install on schedule.

**Initial free disk on $HOME:** 157G

## Virtual environment
- Path: ~/Documents/workspace/sensor-fusion/venv_openpcdet
- Python: Python 3.10.12
- pip: 26.1.1

## OpenPCDet
- Repo: https://github.com/open-mmlab/OpenPCDet
- Cloned at: 2026-05-27 10:30:02
- Commit: `233f849829b6ac19afb8af8837a0246890908755`
- Branch: master

## PyTorch on Jetson
- Source: Jetson AI Lab devpi mirror `https://pypi.jetson-ai-lab.io/jp6/cu126` (canonical for JP6.2 + CUDA 12.6 + Python 3.10 as of 2026-05).
- torch: 2.8.0
- torchvision: 0.23.0
- CUDA build: 12.6
- cuDNN version: 90300
- CUDA available: True
- GPU device: Orin
- compute capability: (8, 7)  - i.e. `sm_87`, the Ampere-Jetson capability that all downstream source builds (cumm, spconv, OpenPCDet ops) target.
- numpy pinned at install time: 1.26.4 (the JPL torch 2.8.0 wheel was compiled against numpy 1.x's C-API; numpy 2.x breaks the torch↔numpy bridge - see Issues §1).

- pip freeze saved to: docs/d12_pip_freeze.txt (189 packages pinned)

## spconv and cumm (built from source - no pre-built aarch64 wheels exist)

No aarch64 pre-built wheel exists for spconv 2.3.8 or cumm 0.7.x on PyPI; the PyPI `spconv-cu120` series is x86_64-only. Built from source on the Jetson:

### cumm 0.7.13
- Source: https://github.com/FindDefinition/cumm (`master` at clone time = 0.8.2)
- **Version pin required:** spconv 2.3.8 declares `cumm<0.8.0,>=0.7.11` in its `pyproject.toml`. cumm's master had advanced to 0.8.x without spconv being updated. Resolution: `git checkout v0.7.13` (the highest 0.7.x tag) before building.
- Install command (final working): `pip install . --no-build-isolation`  (the `-e` flag fails - cumm's `setup.py` predates PEP 660; non-editable install is fine)
- Build artefacts copied manually into the venv (see Issues §3):
  - `cumm/include/` → `<venv>/lib/python3.10/site-packages/cumm/include/`
  - `cumm/build/` → `<venv>/lib/python3.10/site-packages/cumm/build/`
  - `cumm/core_cc.cpython-310-aarch64-linux-gnu.so` → `<venv>/lib/python3.10/site-packages/cumm/`  (the package-root .so is what Python imports as `cumm.core_cc`; the build/ tree is intermediate)
- Verified: `python -c "import cumm; print(cumm.__version__)"` → `0.7.13`; `from cumm import tensorview as tv` clean.

### spconv 2.3.8
- Source: https://github.com/traveller59/spconv (`master` at clone time = 2.3.8)
- Build env vars (REQUIRED - without these, the build silently produces an empty 180 KB Python-only wheel with no CUDA kernels):
  - `SPCONV_DISABLE_JIT="1"` (counter-intuitively named: disables runtime JIT and forces build-time CUDA kernel compilation)
  - `CUMM_CUDA_ARCH_LIST="8.7"` (target sm_87)
  - `TORCH_CUDA_ARCH_LIST="8.7"`
  - `MAX_JOBS=2` (without this, the build OOMs on a 16 GB Orin NX partway through NVCC)
- Install command: `pip install . --no-build-isolation`
- Build duration: ~25 min wall-clock (mostly silent NVCC compilation of convolution kernel variants - DO NOT cancel even when terminal output appears stuck for many minutes between checkpoints).
- Wheel produced: `spconv-2.3.8-cp310-cp310-linux_aarch64.whl`, **11.17 MB** (vs the 180 KB empty-wheel signature of the wrong build).
- Verified end-to-end: spconv 2.3.8 imports, `SparseConvTensor` constructed on CUDA, `dense()` returned `torch.Size([1, 1, 4, 4, 4])` correctly.

## OpenPCDet itself
- Install command: `python setup.py develop` (with the same `CUMM_CUDA_ARCH_LIST="8.7"`, `TORCH_CUDA_ARCH_LIST="8.7"`, `MAX_JOBS=2` env vars exported; setup.py is pre-PEP-660 so `pip install -e .` fails, but `setup.py develop` works - installs as an egg-link pointing back to the source tree)
- pcdet version: `0.6.0+233f849` (git SHA embedded into `__version__` at install time)
- CUDA ops compiled and loaded: `iou3d_nms_cuda`, `roiaware_pool3d_cuda` (and the rest of `pcdet/ops/*`)
- Build duration: ~10 min

### Patch applied: `pcdet/datasets/__init__.py` line 15
Wrapped the unconditional `from .argo2.argo2_dataset import Argo2Dataset` in `try/except (ImportError, RuntimeError)` so the import becomes optional. Original kept as `__init__.py.bak`. Rationale: the Argo2 import chain pulls `av2 → kornia 0.8.2`, and kornia 0.8.2's `quaternion_to_rotation_matrix` has a torchscript compilation bug under torch 2.8 (`cannot statically infer the expected size of a list in this context`). Argoverse 2 is not used in this thesis (we use nuScenes-pretrained PointPillars-MultiHead), so the patch is a clean no-op for our pipeline. Without it, **every** `pcdet.datasets` import fails - including the nuScenes path needed for Day 6.

After patch: `from pcdet.datasets import KittiDataset, NuScenesDataset` imports cleanly; `Argo2Dataset` is the symbol `None`.

## KITTI install-sanity demo (§5.5)
- Outcome: **SKIPPED**
- Reason: install correctness already proven by other channels - `pcdet` imports cleanly, both CUDA ops loaded (`iou3d_nms`, `roiaware_pool3d`), `torch.cuda.is_available()` returns True, and the spconv `SparseConvTensor` smoke test passed end-to-end. Running the KITTI demo would also have required (a) downloading a `000000.bin` KITTI sample (not in the repo), (b) installing open3d (done, 0.18.0), (c) installing matplotlib (done, 3.10.9), and (d) the Argo2 patch above. After (a)–(d) the demo would have run KITTI-pretrained PointPillar inference - but **KITTI is not the working dataset for this thesis** (nuScenes is, per Decisions Log 2026-05-19). The demo would have validated a code path we don't use.
- Side-effect: open3d (0.18.0) and matplotlib (3.10.9) installed during the chase remain in the venv. open3d will be useful in Week 3+ for visualizing fused detections; matplotlib is a common transitive requirement anyway.

## nuScenes PointPillars-MultiHead checkpoint
- Source: OpenPCDet Model Zoo, NuScenes baselines table, PointPillar-MultiHead row → Google Drive `https://drive.google.com/file/d/1p-501mTWsq0G9RzroTWSXreIMyTUUpBM/view?usp=sharing`
- Config (already in the OpenPCDet repo clone): `tools/cfgs/nuscenes_models/cbgs_pp_multihead.yaml`
- Filename: pp_multihead_nds5823_updated.pth
- Size: 24M
- SHA256: 0d241edcfc089a1d1901c2747ea9cb8cb3eec80c9e86a551727ac526e063e77d
- Downloaded at: 2026-05-27 14:05:01
- Published performance on nuScenes val: mAP 44.63 / NDS 58.23 (mATE 33.87, mASE 26.00, mAOE 32.07, mAVE 28.74, mAAE 20.15)

## Issues encountered (compact index - full diagnostic narrative in `week02_log.md` Day 5 Errors & solutions)

1. **Numpy ping-pong.** The JPL torch 2.8.0 wheel needs `numpy<2`. Three subsequent pip installs each re-upgraded numpy: opencv-python 4.13.0.92 (metadata-pinned `numpy>=2`), av2 0.3.6 (transitively via kornia), and OpenPCDet's `setup.py develop` (resolver picked the newest numpy that satisfied its loose `>=1.23` pin). Symptom on every re-upgrade: `UserWarning: Failed to initialize NumPy: A module that was compiled using NumPy 1.x cannot be run in NumPy 2.x` on `import torch`, followed by silent corruption of every `tensor.numpy()` call downstream. Durable fix: pin `opencv-python<4.10` (4.9.0.80 doesn't require numpy 2.x), remove `av2`/`kornia` after applying the Argo2 patch, re-pin `numpy<2` after any future install that touches transitive deps. Operational rule: `pip freeze | grep numpy` after every pip install.
2. **PEP 660 / editable-install failures on cumm and spconv.** Both repos use `setup.py`/`pyproject.toml` predating PEP 660; `pip install -e .` returns `ERROR: Project ... uses a build backend that is missing the 'build_editable' hook`. Fix: use `pip install . --no-build-isolation` (no `-e`). For OpenPCDet itself, `python setup.py develop` is the editable equivalent and works.
3. **cumm packaging gaps.** cumm's `setup.py` doesn't declare its C++ include directory or its compiled `core_cc.so` extension as package data; both end up at the source tree's package root after the first JIT build but not in the installed wheel. Symptom: `AssertionError` at `cumm/constants.py:35` (missing `TENSORVIEW_INCLUDE_PATH`), then `ModuleNotFoundError: No module named 'cumm.core_cc'`. Fix: manually copy `cumm/include/` and `cumm/core_cc.cpython-310-aarch64-linux-gnu.so` from the source tree to the venv's site-packages cumm directory.
4. **cumm version skew vs spconv pin.** cumm master at clone time was 0.8.2; spconv 2.3.8 requires `cumm<0.8.0,>=0.7.11`. Fix: checkout cumm tag `v0.7.13` (the highest 0.7.x release) before building cumm.
5. **spconv produced an empty wheel without the right env vars.** The default `pip install .` for spconv yields a 180 KB Python-only wheel - no CUDA kernels. The build needs `SPCONV_DISABLE_JIT="1"` + `CUMM_CUDA_ARCH_LIST="8.7"` exported in the environment. With those set, the wheel is 11.17 MB and contains the compiled `spconv.core_cc.so` for sm_87. Build takes ~25 min on Orin NX with `MAX_JOBS=2`.
6. **spconv build OOM on Orin NX without job cap.** Without `MAX_JOBS=2`, parallel NVCC compilation peaks above the 16 GB memory ceiling. Symptom: build aborts mid-way with `internal compiler error: Killed (program cc1plus)`. Cap to 2; build is slower but completes.
7. **spconv build appearing stuck for many minutes between checkpoints.** Two builds were cancelled at ~20 min wall-clock because the terminal showed no progress; the third (after capping MAX_JOBS=2) was left running and completed at ~25 min. Lesson: NVCC compilation phases of spconv produce almost no terminal output; only cancel if `top` shows no NVCC activity for >5 min.
8. **OpenPCDet's `pcdet/datasets/__init__.py` unconditionally imports Argo2.** The Argo2 import chain pulls `av2 → kornia 0.8.2`; kornia 0.8.2's `quaternion_to_rotation_matrix` triggers a torchscript compile error under torch 2.8 (`cannot statically infer the expected size of a list in this context`). This blocks `import pcdet.datasets` entirely - including the nuScenes code path. Fix: wrap the Argo2 import in `try/except (ImportError, RuntimeError)`, set `Argo2Dataset = None` on failure. We don't use Argoverse 2 in this thesis.

## Final state (14:05:16)
- Free disk on $HOME: 153G  (delta: ~4 GB consumed by venv + cumm/spconv builds + open3d/matplotlib/cumulative pip cache)
- Decision for Day 6: **proceed with nuScenes PointPillars-MultiHead**. All install gates clear; checkpoint downloaded and SHA-pinned. Day 6 work (bag-frame to OpenPCDet `.bin` conversion + nuScenes-pretrained inference) starts on schedule against the slipped-but-stable Week 2 baseline.
