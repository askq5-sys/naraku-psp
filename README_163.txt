NARAKU PSP 1.6.3 - Underground route and cinematic framing

Requires the complete 1.6.2 installation. Saves and configuration are retained.

Presentation fixes:
- Map 094 dealers fade out as they leave the right-hand cinematic frame. Their original forced routes, contact and event state remain intact.
- Maps 098 and 099 frame the staged action rather than the offscreen player. Dialog and picture coordinates are unchanged.

Added original underground maps 100-104: entry from alley 086, connected rooms, original switches, interactions, scripted movements, pictures, audio and END 7/7 A Step Before the Abnormal.
Added command 105/405 scrolling text, including all 31 original epilogue lines in all four languages, original speed and optional fast-forward. Original transparent ending captions are preserved.

This is an alternate city route, not an automatic continuation after END 5. Load an in-game save before the city branch, explore the baton purchase route and follow its original events. Access from alley 086 requires switch 935, set by the original return-home scene on map 089. No ending flags are forced.
Other guarded city interiors and routes remain outside this patch. This does not claim the whole Will chapter is finished.

Validation: 716 original/adapted event pages, passability, conditions, exact command bytes and resource dependencies; actual C cinematic camera checks; all scrolling epilogue lines in four languages; actual dealer route replay, autonomous pursuer routes, save thumbnails, giant-spider escape, dialogue styling, host C syntax and deployment script syntax.
No PSP SDK linking or PPSSPP/real PSP playthrough was available here.

Install from the project directory:
  unzip -t /mnt/c/Users/Rgood/Downloads/naraku_psp_1.6.3_underground_patch.zip
  unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.6.3_underground_patch.zip
  chmod +x tools/build_deploy_v163.sh
  ./tools/build_deploy_v163.sh

Fully restart the game and load an in-game save, not an emulator save state. Use a save before the relevant scene to replay its events.
The deployment script copies only listed changed runtime assets and EBOOT.PBP. No runtime compression or save deletion is performed.
