NARAKU PSP 1.6.5 - Will street cinematic exit
Requires 1.6.4. Saves, configuration and assets are retained.

In Map 096, Will becomes visually hidden as soon as his original rightward run reaches the final map tile. The pursuers' script continues normally. This is a local rendering rule; original coordinates, movement, party visibility state and subsequent scenes are retained.

Validation: host C syntax, deployment shell syntax and original dealer route replay. PPSSPP/PSP runtime testing was not available.

Install from the project directory:
  unzip -t /mnt/c/Users/Rgood/Downloads/naraku_psp_1.6.5_street_exit_patch.zip
  unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.6.5_street_exit_patch.zip
  chmod +x tools/build_deploy_v165.sh
  ./tools/build_deploy_v165.sh

Fully restart the game and replay from an in-game save before the scene.
