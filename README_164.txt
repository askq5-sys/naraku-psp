NARAKU PSP 1.6.4 - Rooftop vertical camera fix
Requires 1.6.3. Saves, configuration and assets are retained.

Map 098 now starts its scripted vertical pan from the bounded initial viewport, instead of adding the pan to hidden Will's offscreen centre. The rooftop actor's entire body fits above the dialogue window. Horizontal framing from 1.6.3 is retained. This change is scoped to this cinematic map.

The brief darkening before Will's panting dialogue on Map 095 is original: tint to black over 5 frames, wait, transfer, wait, then restore normal tint over 5 frames. It is intentionally retained.

Validation: actual C camera fixture verifies the final viewport and full actor height; city camera regression; original epilogue text payload; host C syntax and deployment shell syntax. PPSSPP/PSP runtime testing was not available.

Install from the project directory:
  unzip -t /mnt/c/Users/Rgood/Downloads/naraku_psp_1.6.4_rooftop_camera_patch.zip
  unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.6.4_rooftop_camera_patch.zip
  chmod +x tools/build_deploy_v164.sh
  ./tools/build_deploy_v164.sh

Fully restart the game and load an in-game save before the scene. Do not use an emulator save state for this test.
