NARAKU PSP 1.3.0 — killer walking in the hatch escape cutscene
Cumulative over 1.2.9.

Map035 event7's visible walking pose now follows distance travelled during its
forced speed5 route: original sequence 1,2,1,0, one change per walked tile
(eight movement frames at speed5). This applies to the seven steps up and the
later thirteen steps right. Wait/look-around commands and completed routes
retain the regular idle state. The original route, directions, waits, speed,
collision and timing are unchanged. Fresh Map035 event graphics included.

Validation: actual C renderer checks every up/right step, pause and route end;
factory original command/route comparisons and graphics/collision audits passed.
No PSP SDK / PPSSPP available here: runtime behavior still needs checking.

Install with PPSSPP closed:
cd ~/projects/naraku-psp
unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.3.0_escape_walk_patch.zip
chmod +x tools/build_deploy_v130.sh
./tools/build_deploy_v130.sh

Fully restart; use an in-game save rather than an old emulator savestate.
