NARAKU PSP 1.3.4 - Factory dialogue and elevator flashback patch

Apply over a complete 1.3.3 project/installation. This is a delta patch,
not a complete game download. Close PPSSPP before deploying.

Changes
- Corpse barricades on Maps033/034 retain more fine detail with filtered
  sampling. Display sizes and collision pages are unchanged.
- Remove RPG Maker font-size directives from dialogue before wrapping;
  keep actual dialogue, colors and punctuation. Runtime filtering also
  handles older installed dialogue resources.
- All 60 Map039 messages fit one three-row window at the current font size.
- Restore capital Cleaver in Oliver's flashback line, preserving red color.
- Compile the Map047 elevator flashback in full: the already implemented
  event direction-lock/unlock commands are now accepted by the converter.
- Refresh Map046/047 event pages and Map047 actor/elevator graphics;
  include walking frames, portraits and exact sound variants.
- Barricade ambush and killer autonomous routes retain the 1.3.3 logic.

Installation (WSL)
cd ~/projects/naraku-psp
unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.3.4_factory_flashback_patch.zip
chmod +x tools/build_deploy_v134.sh
./tools/build_deploy_v134.sh

Verification
Host C tests cover text layout, the actual route direction lock/unlock,
walking animation, chase contact, factory scheduling and portrait/atlas
sampling. Original event page bytecode and picture/audio references on
Maps046/047 are checked. Existing dialogue and factory regression tests
pass. Tests require the original game data and previous resource baselines.

PSP compilation, device performance and full PPSSPP scene playback have
not been verified in this environment. Test from an in-game save before
entering the flashback; emulator snapshots retain the old executable/state.
No asset compression or save/config deletion is performed.
