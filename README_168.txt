NARAKU PSP 1.6.8 - Rooftop actor exit
Requires 1.6.7. Saves, configuration and assets are retained.

Map 098 actor 1 is hidden as soon as the original rightward withdrawal reaches its last tile, x=17. Original walking route, fade timing and event state remain unchanged. Roof-aligned vertical framing and rightward offset are retained.

Validation: host C syntax, deployment shell syntax and cinematic camera regression. PPSSPP/PSP runtime testing was not available.

Install from the project directory:
  unzip -t /mnt/c/Users/Rgood/Downloads/naraku_psp_1.6.8_rooftop_exit_patch.zip
  unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.6.8_rooftop_exit_patch.zip
  chmod +x tools/build_deploy_v168.sh
  ./tools/build_deploy_v168.sh

Fully restart the game and replay from an in-game save before the scene.
