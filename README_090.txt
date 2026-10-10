NARAKU PSP 0.9.0 — explicit framebuffer readback
Uses GE CopyImage from completed world framebuffer to RAM, then synchronizes
before downsampling. Avoids CPU reading stale VRAM under buffered emulation.
Flushes the texture cache before drawing the newly generated background.
Fresh blurred current-location snapshot on each menu opening.
Install over full game using tools/build_deploy_v090.sh.
Fully stop and restart PPSSPP game. Do not load emulator savestates from older
builds: use in-game saves or New Game for verification.
Host route/animation and C syntax checks passed; PSP runtime not available.
