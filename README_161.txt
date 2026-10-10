NARAKU PSP 1.6.1 - Will backstreet story route

Requires 1.6.0. Keeps saves and configuration intact.

Average Days in the Capital (END 4/7) is a finished alternate ending in the original game. It returns to the title screen. Load an in-game save before the ending and explore the other city route.

Added original maps 093-099 and the connecting backstreet map 115: the dealers encounter, chase corridor, main-street scene and subsequent finale. Restored the original exits from maps 089 and 090. Includes the routes leading to END 5/7 The Shadow Behind and END 6/7 Lost Memories, with original conditions, dialogs, switches and catch events. Map 097 is an intermediate scene background: its interpreter continues from map 096, as in the original.

All five autonomous pursuers now use their original routes and native directional walking frames. Added command 213 balloon playback using the original animated balloon texture. The new route can switch Will to actor 008, which now has its own native atlas, compatible PG60 save bits and correct slot thumbnail. Earlier saves remain readable.

The dealer scene retains native source pixels with a different sheet arrangement to fit two texture pages. No runtime texture/audio compression is introduced.

Further underground routes, special streets and unrelated building interiors remain outside this patch. Their boundaries are still guarded; the entire Will chapter is not complete.

Validation: 640 original/adapted event pages, passability, conditions, command bytes, resource dependencies, actor save round trips; actual C autonomous route scheduler activation, page cancellation and pause; all five original route byte sequences; native walking sheets and 80 original balloon frames; existing save-preview, giant-spider and dialogue checks; host C syntax and build-script syntax. PSP linking and real PPSSPP/PSP playthrough remain untested here.

Install:
  unzip -t /mnt/c/Users/Rgood/Downloads/naraku_psp_1.6.1_will_backstreet_patch.zip
  unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.6.1_will_backstreet_patch.zip
  chmod +x tools/build_deploy_v161.sh
  ./tools/build_deploy_v161.sh

Completely restart the game and load an in-game save, not an emulator save state.
