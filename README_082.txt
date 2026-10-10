NARAKU PSP 0.8.2 — player animation / route maintenance patch
Requires a previously deployed full game. Includes all 0.8.1 title-menu changes.

Fixed:
- Player move-route command 13 moves backward and preserves facing (was forward).
  It occurs 101 times in the original Player routes, across 21 maps.
- Direction Fix is honored by manual movement, synchronous turns and jumps.
- One persistent animation state across input, synchronous and asynchronous routes.
  Integer half-unit MZ counter preserves phase across speed/control changes.
- Arrival frame does not reset to standing between adjacent tile commands.
- Walk/Step flags and stopped recovery use original animation-count logic.
- Asynchronous routes remain inside map bounds even with Through enabled.
- Final asynchronous visibility/direction commands apply in the same render frame.
- Defensive frame/row bounds prevent reading outside the character atlas.

Maintenance:
- Animation and route delta helpers extracted to runtime/player_animation.h.
- Removed duplicated walk counters, sequences and unused local a1 alias.
- Split misleadingly indented color-clamp statements without behavior changes.
- Deploy failure now reports the successfully built file and manual destination.
- Save format, existing assets, pixel-art filter fix, keys and XMB preserved.

Validation performed:
- 25,200 deterministic frames: speeds 1..7, Walk/Step on/off, walking then stopping.
- 100,000 mixed animation updates against original MZ arithmetic.
- Actual asynchronous route tick: backward facing, last frame, blocked direction,
  Direction Fix, Through at map bounds.
- Rebuilt original character atlas: 12 frames, 48x78 sources, visible edge gutters.
  Transparent pixels may carry different invisible RGB; comparisons account for alpha.
- Host C syntax check with PSP API stubs; shell syntax and host tests.
No PSP SDK/emulator available here: real PSP build and visual hardware QA remain.
This is targeted runtime maintenance, not a claim of complete game-wide MZ parity.
Legacy compatibility helpers are retained; some unused-function warnings may remain.

Install in WSL (close PPSSPP first):
cd ~/projects/naraku-psp
unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_0.8.2_animation_patch.zip
chmod +x tools/build_deploy_v082.sh
./tools/build_deploy_v082.sh

Optional host checks (requires cc and Python 3):
bash tests/run_host_checks.sh

Hardware visual checklist:
1. Hold each direction across several tiles; stop, reverse, move against a wall.
2. Walk/run and toggle Always Dash; enter speed-changing terrain.
3. Dialogue at tile arrival; repeated dialogues; inventory/save/load and return.
4. Event-controlled walks and backward moves; Direction Fix scenes.
5. Jumps, hide/show, fades and map transfers; first movement after loading.
Check for frame flashes, foot/camera jitter, sprite-edge halos and wrong facing.
