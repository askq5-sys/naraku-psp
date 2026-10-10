NARAKU PSP 1.4.0 - Factory lever timeout reset

Requires the complete game and patch 1.3.9.
Unzip into the project, then run tools/build_deploy_v140.sh.
Restart and load an in-game save; avoid older emulator save states.

The original Map049 event16 changes from a parallel 200-frame timer to an
autorun reset after its timeout beep. The PSP timer ran correctly, but the
autorun dispatcher was only called after actions and transfers. Consequently,
an idle player could hear the beep while lever progress stayed active.

The frame scheduler now runs that exact reset page on the next update,
without requiring input or interrupting movement. This page only writes
switches and plays one sound. It retains the existing 1.3.7 correction that
also clears the fifth checkpoint and incomplete door progress.
All other autorun pages continue through their existing dispatcher.

Validation: actual packed Map049 resources and C scheduler tested for an
idle timeout after the second checkpoint, all checkpoint resets, a fresh
retry timer, cancelled/completed timers and unrelated inventory retention.
Existing stage timing, native sprite and Rope checks pass. Whole main.c
passes host syntax checking with PSP API stubs. No PSP runtime verification
was available here. Resources and the save format are unchanged.
