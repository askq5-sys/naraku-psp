NARAKU PSP 1.2.1 cumulative patch

Plant1 Map009: move armed worm encounter from flesh wall event 4 at (28,18) to invisible floor event 15 at (28,21), three tiles south. Switch22 condition retained; unarmed footsteps retained. Keep wall graphic and remove only its armed interaction. Remove initial black tint and self-transfer backwards; retain normal approach, dialogue, worm graphics/routes/sounds/death sequence.
Used the gold key: lowercase inside sentence; gold palette14; all prior key styling fixes retained.
All host regression tests passed; PSP build/runtime not available here.

Close PPSSPP, update and launch from a full stop. Use an in-game save to test updated code rather than an old emulator state.
cd ~/projects/naraku-psp
unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.2.1_plant1_trigger_patch.zip
chmod +x tools/build_deploy_v121.sh
./tools/build_deploy_v121.sh
