NARAKU PSP 1.6.9 - Ending 6 chase approach
Requires 1.6.8. Saves, configuration and assets are retained.

Only during the last westward approach to the meeting on Map 095 (Ending 6 branch, switch 939), autonomous pursuers gradually take longer steps as Will approaches the exit. The adjustment begins inside the final eight tiles, rows 12-16, reaching at most 50% extra step duration. This lets Will develop a small lead before the original scene removes the pursuers.

Original routes, catch collisions, branch conditions, disappearance switches and forced cutscene movements are retained. Other chase sections and endings are unchanged.

Validation: host C syntax, deployment shell syntax, autonomous pursuer scheduler and original dealer scene route replay. PPSSPP/PSP runtime testing was not available.

Install from the project directory:
  unzip -t /mnt/c/Users/Rgood/Downloads/naraku_psp_1.6.9_ending6_chase_patch.zip
  unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.6.9_ending6_chase_patch.zip
  chmod +x tools/build_deploy_v169.sh
  ./tools/build_deploy_v169.sh

Fully restart the game and replay from an in-game save before the chase.
