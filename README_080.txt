NARAKU PSP 0.8.0 — responsive title navigation
Apply over 0.7.9 (including optional XMB artwork patch):
  cd ~/projects/naraku-psp
  unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_0.8.0_menu_patch.zip
  chmod +x tools/build_deploy_v080.sh
  ./tools/build_deploy_v080.sh

Changes: immediate new press/direction change; hold repeats after 400 ms then
at 100 ms intervals (24/6 frames at 60 Hz); input handled before rendering;
no save-file probing per frame. Directions held on scene entry remain ignored
until released. Existing XMB CMake settings, game assets and saves are preserved.
The script updates the CMake VERSION to 00.80 and builds in build_menu080.
Gameplay code after the menu section is byte-for-byte unchanged.

Checks: actual C navigation helper tested with a fake clock (initial press,
repeat boundaries, immediate reversal, release/repress, opposite keys, entry
with a held key). Shell syntax and host C syntax checked.
PSP linking and real-device input response were not tested here.
