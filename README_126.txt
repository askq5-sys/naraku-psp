NARAKU PSP 1.2.6 — second school flashback, cumulative over 1.2.5

Scope: Maps028-031 (alternative escape landing, second memory corridor,
school flashback, connection/save passage). The factory chase beginning at
Map032 is the following block and is not completed by this patch.

Current-stage audit (Maps014-027):
- All 536 event pages accounted for: 535 compiled, one Map024 press-cycle
  parallel page handled by the existing dedicated tested runtime.
- Every visible source page now has its sprite reference. Found and restored
  the three missing door states in Map022 (first execution room).
- Prior key, worm, chase, ladder, tentacle death, laser and press fixes retained.

New block:
- All 30 source event pages compiled (1+14+11+4), with original commands,
  item/switch gates, choices, waits, transfers and one-shot memory switches.
- NPC jumps implemented with the original MZ jump peak/height timing, including
  Lucas's two on-the-spot jumps and their wait interval.
- Emma/Enri use three walking patterns in all four directions at source resolution.
- Other classroom characters retain source frames; sprites sort by foot Y.
- Non-waiting camera scrolls now run over time concurrently with move routes;
  waiting scrolls use the same frame timing.
- 43 original flashback messages checked for lossless English reflow.
- Required portraits included with existing resource IDs; new Wish BGM PCM variant
  included without renumbering any earlier audio. Assets remain uncompressed at runtime.

Validation: complete page/sprite-reference audit, source command comparison,
portrait/audio presence, atlas bounds, original one-shot gates, host C NPC jump
and scroll timing tests, text reflow and earlier regression tests passed.
No PSP SDK / PPSSPP available here: device compilation, visuals and gameplay
still need runtime verification.

Install with PPSSPP closed:
cd ~/projects/naraku-psp
unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.2.6_second_flashback_patch.zip
chmod +x tools/build_deploy_v126.sh
./tools/build_deploy_v126.sh

Restart the game fully. Use an in-game save/new run rather than an old emulator
save state. Normal progress: through the second shutter into the memory corridor,
finish the classroom scene, return and walk onward to the connection/save passage.
