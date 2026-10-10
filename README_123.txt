NARAKU PSP 1.2.3 — cumulative patch over 1.2.2

English dialogue:
- Sentence-aware lowercase cleaver with existing colour preserved.
- English whitespace collapsed, source PC line breaks reflowed to PSP font widths.
- Colour and auto-close controls no longer bypass reflow or consume text width.
- Emma material delivery message retains its complete question in three lines.

Rendering:
- Opening Enri falling event uses continuous actor camera instead of rounded tile camera.
- Settled opening sprites align to the pixel grid; jump rendering stays continuous.
- Hanging figures on Maps 021/023/027 use 36x144 filtered source frames instead of
  24x96 nearest-downsampled frames. Final display size remains 24x96.
  Native 48x192 strips do not fit the single 512x512 PSP atlas on Map021.
- Original fall poses are retained; their art differs from the ordinary walk sheet.

Plant1 third-tile worm trigger and prior fixes are preserved.

Validation: host C text/runtime regressions, source sprite resampling/atlas bounds,
Python converter compilation and deployment shell syntax checked.
PSP SDK / PPSSPP are unavailable here; device build, visual runtime and frame rate
must be checked after installation.

Install from ~/projects/naraku-psp:
unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.2.3_text_fall_sprites_patch.zip
chmod +x tools/build_deploy_v123.sh
./tools/build_deploy_v123.sh

Close PPSSPP before deploying. Fully restart the game after deploying; old emulator
save states can restore old code/resources. Use an in-game save or a new run to test.
