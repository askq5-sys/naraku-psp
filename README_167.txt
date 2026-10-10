NARAKU PSP 1.6.7 - Roof-aligned cinematic pan
Requires 1.6.6. Saves, configuration and assets are retained.

Map 098 upward pan stops at source row 6, the actual first visible roof row. The roof aligns with the top of the screen instead of exposing empty black map space above it. The rightward offset is retained and the rooftop actor stays fully visible. Original event timing and gameplay coordinates are unchanged.

Validation: original map geometry, actual C camera fixture verifies roof/top alignment and full actor visibility, host C syntax and deployment shell syntax. PPSSPP/PSP runtime testing was not available.

Install from the project directory:
  unzip -t /mnt/c/Users/Rgood/Downloads/naraku_psp_1.6.7_roof_pan_patch.zip
  unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.6.7_roof_pan_patch.zip
  chmod +x tools/build_deploy_v167.sh
  ./tools/build_deploy_v167.sh

Fully restart the game and replay from an in-game save before the scene.
