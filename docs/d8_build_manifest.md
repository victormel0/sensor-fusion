# Day 1 build manifest -- 2026-05-19
**Note:** captured post-hoc; build wall-times are estimates from memory.

## GTSAM
- Commit: `c57988fe554e7213c77fe379c1d7c483de26ad33`
- Tag: 4.2a9
- Build time: ~15 min

## Ceres-Solver
- Commit: `e47a42c2957951c9fafcca9995d9927e15557069`
- Build time: ~10 min<estimate from memory; note: rebuilt once after BUILD_SHARED_LIBS fix>

## Iridescence
- Commit: `a3d11ffe9fc01c216856aa3b40396b1d8fd64b05`
- Build time: ~7 min

## Install verification (22:41:07)
- ldconfig entries:
    	libiridescence.so.1 (libc6,AArch64) => /usr/local/lib/libiridescence.so.1
    	libiridescence.so (libc6,AArch64) => /usr/local/lib/libiridescence.so
    	libgtsam_unstable.so.4 (libc6,AArch64) => /usr/local/lib/libgtsam_unstable.so.4
    	libgtsam_unstable.so (libc6,AArch64) => /usr/local/lib/libgtsam_unstable.so
    	libgtsam.so.4 (libc6,AArch64) => /usr/local/lib/libgtsam.so.4
    	libgtsam.so (libc6,AArch64) => /usr/local/lib/libgtsam.so
    	libceres.so.4 (libc6,AArch64) => /usr/local/lib/libceres.so.4
    	libceres.so (libc6,AArch64) => /usr/local/lib/libceres.so

## System state after builds
- Free disk on $HOME: 190G (of 233G)
- Free RAM: 11Gi (of 15Gi)
