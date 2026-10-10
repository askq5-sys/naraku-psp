NARAKU PSP 1.2.8 — factory press sprite quality
Cumulative over 1.2.7, including the first factory block and previous fixes.

Map032 press machine now stores a filtered 252x288 frame (3/4 of the 336x384
original) instead of the old nearest-neighbour 168x192 frame. GU linear filtering
renders it at the same 168x192 display size, preserving position and collisions.
It fits in the existing 512x512 event atlas: no extra runtime texture allocation.

Validated exact source-resampling pixels, display dimensions, atlas bounds,
factory command streams/routes, references and machine timing. No PSP/PPSSPP
runtime available here; visual appearance still needs testing on the device.

Close PPSSPP, install and restart using an in-game save rather than old savestate:
cd ~/projects/naraku-psp
unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.2.8_machine_sprite_patch.zip
chmod +x tools/build_deploy_v128.sh
./tools/build_deploy_v128.sh
