NARAKU PSP 1.3.6 — factory notes, save books and elevator junction

Apply over a complete 1.3.3, 1.3.4 or 1.3.5 installation. This cumulative
patch includes the previous 1.3.4/1.3.5 changes.

Changes:
- Password-note pictures use a black backdrop across the whole PSP viewport.
- Direct Save calls from scripted books open the slot screen even when the
  ordinary menu Save command is disabled, matching RPG Maker's scene calls.
  The opening button must still be released before a slot can be confirmed.
- Corpse barricades use original-resolution sprite pixels with linear GPU
  sampling. Removed the previous repeated downsample/upscale blur.
- Event depth sorting includes the original object/character foot offset;
  elevator doors draw over Enri when she occupies their tile.
- After the junction lever destruction scene (switch 632), only the lever
  base is drawn; its handle disappears. The original lowered lever tile was
  unchanged after destruction, so this visual feedback is a port addition.
- Added original map 056–058 resources, event pages, elevator lever states,
  transfers, save-book marker and audio dependencies.
- The third left lever in map 048 was checked against original data. Its
  initial English reply is "It won't work."; this reply was retained.

Installation in WSL:
cd ~/projects/naraku-psp
unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.3.6_elevator_fixes_patch.zip
chmod +x tools/build_deploy_v136.sh
./tools/build_deploy_v136.sh

Restart the game executable after deployment. Test from an in-game save,
not a PPSSPP save state captured with the previous executable.
The script preserves your saves, configuration, XMB files and existing assets.
This patch does not complete or certify the later maps 059 onward.

Validation:
Host tests run the real C save-slot UI, note renderer, sprite renderer/depth
sorting and event scheduler. Original stage page bytes, conditions, collision
masks, atlas bounds and picture/audio dependencies are verified for maps
048–058; earlier factory and flashback regression checks also pass.
No PSP SDK compilation or PSP/PPSSPP visual runtime test was available here.
