NARAKU PSP 1.7.4 - Original message and choice window modes

Every original Show Text and Show Choices command retains its background
and position: normal red-bordered window, dim black backdrop, or transparent
window with visible text. Ending captions use their original invisible window.
Choice windows retain the existing red/black NARAKU style and now use the
original left/center/right placement and background setting.

The build script upgrades installed VM files from previous stages, preserving
sprite references, text bytes, sounds, routes and page conditions. Branch
addresses are relocated and verified. Migration is idempotent and validates
all resources before writing upgraded data. No saves or settings are removed.
The original metadata for all 139 maps is bundled; the original game files
are not needed during installation.

Install over the current project and run tools/build_deploy_v174.sh.
Restart and load an in-game save; do not use an older emulator save state.

Validated: 1,864 window commands in the 98 locally available map resources,
all window metadata and relocated branches; 944 original city pages; runtime
host syntax; gallery interaction. Earlier installed maps are upgraded locally
by the same migration. Visual PSP/PPSSPP playtest still required.
