NARAKU PSP 1.1.8 — cumulative patch

English dialogue: reflow independent of current map ID after transfers; PC-specific wraps removed. Three-row pagination retains full text.
Iron/Red/Green key: sentence-aware capitalization; Red key uses original palette 18, Green key palette 3; surrounding colors restored.
S-003 Maps024/025: original three walking patterns, four facing rows, Lanczos conversion and linear rendering, original custom movement routes and contact while player stands still.
All prior assets and fixes included. Saves retained.

Close PPSSPP before deployment.
cd ~/projects/naraku-psp
unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.1.8_text_enemy_patch.zip
chmod +x tools/build_deploy_v118.sh
./tools/build_deploy_v118.sh

Host regression tests passed. PSP compilation and runtime are not tested in this environment.
