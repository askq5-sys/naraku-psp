NARAKU PSP 0.8.4 — intro fall / slow slide rendering
Includes 0.8.3 and its font assets.

Map001 Event5 is the falling/rolling Enri, distinct from the real Player.
Original pages disable walk/step animation and explicitly switch between poses.
The final movement uses speed2: 24px * 2^2 /256 = 0.375 native PSP pixels/frame.
Rounding to whole pixels makes its visible position change only 22.5 times/sec.

Changes:
- Preserve fractional coordinates for Map001 Event5 only.
- Keep its six original source poses at PC resolution in the event atlas,
  downsampling with linear filtering. Pose count, speeds and waits unchanged.
- Restore pixel-art GPU state after each event sprite; normal map/Player rendering
  retains its existing nearest filtering and integer alignment.
- Sprite may look slightly softer while interpolating at fractional positions.

Validated: identical map gameplay metadata and record order, pixel-identical
other event sprites, doubled source dimensions for six fall poses, host tests,
C syntax using PSP stubs, deployment shell syntax.
PSP SDK/runtime unavailable here. This fixes identified raster stepping;
actual performance/frame pacing and the result on PSP/PPSSPP require runtime QA.

Close PPSSPP, then run in WSL:
cd ~/projects/naraku-psp
unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_0.8.4_fall_patch.zip
chmod +x tools/build_deploy_v084.sh
./tools/build_deploy_v084.sh
