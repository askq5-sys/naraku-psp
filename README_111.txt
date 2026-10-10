NARAKU PSP 1.1.1 cumulative patch over the existing complete game.

Close PPSSPP before deploying.
cd ~/projects/naraku-psp
unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.1.1_scene_visuals_patch.zip
chmod +x tools/build_deploy_v111.sh
./tools/build_deploy_v111.sh

Changes:
- Full walking patterns for flashback Emma carrying a tray.
- Enri's scripted special poses are fixed frames, not walking directions.
- Event page changes refresh facing, direction-fix, through and opacity.
- Direction-fix route commands 35/36 are respected by background NPC routes.
- Visible geometry of Map011 and Map013 is horizontally centred; logical map,
  collision, event coordinates and vertical camera remain unchanged.
- Cleaver on Map013 uses all three original PC-resolution frames with GPU
  linear downsampling; source texture details are not discarded beforehand.
- Includes previous 1.1.0 fixes, font, inventory, scene scripts and audio assets.

Checks: host C regression tests, generated atlas metadata, Python syntax and
shell syntax passed. PSP SDK build and PPSSPP/real-PSP runtime not available here.
Save files are not deleted or rewritten by the deployment script.
