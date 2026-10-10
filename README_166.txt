NARAKU PSP 1.6.6 - Rooftop horizontal framing adjustment
Requires 1.6.5. Saves, configuration and assets are retained.

Moves the Map 098 rooftop scene 24 native PSP pixels to the right (one tile). Retains the corrected vertical pan from 1.6.4. Map 099 and gameplay coordinates are unchanged.

Validation: actual C camera fixture checks the new horizontal anchor and unchanged vertical viewport; host C syntax and deployment shell syntax. PPSSPP/PSP runtime testing was not available.

Install from the project directory:
  unzip -t /mnt/c/Users/Rgood/Downloads/naraku_psp_1.6.6_rooftop_offset_patch.zip
  unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.6.6_rooftop_offset_patch.zip
  chmod +x tools/build_deploy_v166.sh
  ./tools/build_deploy_v166.sh

Fully restart the game and replay from an in-game save before the scene.
