NARAKU PSP 1.2.5 — tentacle-pit death, cumulative over 1.2.4

Map015:
- Dynamic sprite records now include every switch-driven capture, struggle,
  escape and sinking pose for both pit triggers (events 10 and 11).
- Original character frames retained at 48x144 and displayed at PSP half size.
- Existing source choices, condition branches, switches, waits, sounds and
  transfer commands are preserved; no replacement scene timeline is invented.

Map016:
- Switch 132 shows the original falling Enri event; original twelve downward
  steps at event page speed 6 and the death sequence remain in the VM.
- Falling actor retains its original 80x80 frame and continuous actor camera.
- Room sprites sort by their feet Y within their original priority, letting
  the falling Enri disappear behind foreground tentacles as in RPG Maker.
- Oversize room/tentacle artwork uses filtered downsampling within a 512 atlas.

All scene pages compiled (Map015 36/36, Map016 38/38). Exact sound PCM variants
included. Existing inventory, worm, chase, ladder, text, laser and press fixes retained.

Validation: host C rendering-order regression; all generated event command streams
compared with the source compiler; sprite page references, atlas bounds, sound assets;
previous regression tests passed. Python and deployment shell syntax checked.
PSP SDK and PPSSPP are unavailable here: PSP build and visual runtime are untested.

Install with PPSSPP closed:
cd ~/projects/naraku-psp
unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.2.5_tentacle_death_patch.zip
chmod +x tools/build_deploy_v125.sh
./tools/build_deploy_v125.sh

Fully restart the game; verify using an in-game save or new run, not an old
emulator save state (which can restore code/resources from the earlier build).
