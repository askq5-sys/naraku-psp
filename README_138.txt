NARAKU PSP 1.3.8 - Rope inventory correction

Requires the complete 1.3.7 patch to be installed first.

The original Map044 descent consumes item48 (Rope) and finishes by setting
switch351. This patch reconciles inventory with that completion flag after
loading an in-game save, after switch commands, and during world rendering.
It removes stale or duplicate Rope counts after the completed descent and
retains the Rope after the earlier door unlock, as in the original game.
The original Map044 event resource is included to replace stale deployments.
No other inventory items, story flags, saves, configuration or assets change.

Install: unzip into the project, then run tools/build_deploy_v138.sh.
Restart the game and load an in-game save; avoid older emulator save states.
Validated with host C checks and original event-resource comparison.
PSP compilation and runtime testing require the user's SDK/device/emulator.
