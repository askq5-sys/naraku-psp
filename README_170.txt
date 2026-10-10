NARAKU PSP 1.7.0 - Remaining city locations and bonus gallery

Requires the complete 1.6.9 installation. Keeps saves, configuration and all previous patches. No runtime compression is introduced.

Ending numbering: the original END 4/7 is Average Days in the Capital; its route was already included. END 3/7 is Back Alive, END 5/7 The Shadow Behind, END 6/7 Lost Memories and END 7/7 A Step Before the Abnormal.

Added all remaining original city maps 111-114 and 116-139 (28 locations), including bonus/CG gallery access, additional homes and shops, their connected upstairs rooms, side scenes, original choices, inventory changes, switches, transfers, audio and illustrations. Restored previously guarded city exits. Original event conditions are retained; there is no forced unlock of an ending or bonus room.

Added actors 009 and 010, the native side-view Will forms, with all 12 frames each. New scripted event sheets preserve directional walking animation and native source pixels. Original rotating NPC behavior on Map 120 is included.

Compatible PG60 saves now retain the two extra actor membership bits in unused upper bits of the movement-speed byte. Older saves still load with their original actor and speed. Slot thumbnails support both new forms without modifying the active party. The save file layout and playtime offset remain unchanged. Earlier executables do not support these extra forms; use this version to load saves made in the new scenes.

Gallery illustrations are fitted inside the PSP screen with linear filtering, including existing portrait-format CG resources, instead of cropping the original canvas. Dialogue and gameplay rendering outside the gallery are unchanged.

This completes the previously withheld city map coverage. It is not a claim of a fully tested, bug-free port or a verified all-ending playthrough. Replay the new branches using in-game saves before their original triggers. PSP/PPSSPP runtime testing was not available here.

Validation: 944 original post-credits/city event pages, passability, conditions, bytecode, atlas bounds and referenced assets; no remaining city boundary guards; 48 native alternate Will frames; original autonomous rotating route; actual slot metadata and thumbnail caching for all eight supported actor forms; autonomous pursuers, dealer scene replay, cinematic camera, dialogue styling; host C syntax and deployment shell syntax.

Install from the project directory:
  unzip -t /mnt/c/Users/Rgood/Downloads/naraku_psp_1.7.0_remaining_city_patch.zip
  unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.7.0_remaining_city_patch.zip
  chmod +x tools/build_deploy_v170.sh
  ./tools/build_deploy_v170.sh

Fully restart the game and load an in-game save, not an emulator save state. The script deploys only listed changed runtime assets and EBOOT.PBP; it does not delete saves or configuration.
