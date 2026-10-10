NARAKU PSP 0.8.5 — word wrapping, choices, player raster motion
Includes previous 0.8.4 fixes and assets.

Speed audit: original speed4 normal floor (16 frames/tile), speed5 dash
(8 frames/tile). At60fps:3.75 and7.5 tiles/sec. PSP distances0.5x original pixels,
so1.5 and3 native pixels/frame. Speed3 blood:32 frames/tile, dash speed4:16.
No movement speed values changed.

Text:
- Latin words wrap as units in both software dialogue raster and GU text paths.
  Very long words wider than a complete line retain the emergency glyph wrap.
- Dialogue box now supports three rows, so source explicit line breaks no longer
  clip 'shutter.' in the two-key message. Original translated wording retained.
- English Cleaver changed to cleaver in dialogue bytecode using same-size edit;
  offsets, command lengths and rich-text colour escapes are untouched.
- Choice labels shifted upward4 native pixels, still left-aligned.

Motion:
- Actual Player draws at fractional world positions with source-resolution
  bilinear sampling, covering manual walking and scripted player routes alike.
- Immediately restore the pixel-art texture state after the player draw.
  Maps retain nearest filtering/integer camera alignment and existing halo fix.
- This may soften the Player sprite slightly during fractional motion.
- Does not claim to fix measured frame-rate drops: runtime timing unavailable.

controls_reference contains exact original A2 PNG816x624 and editable draft
SVG480x272 for PSP. Original text is baked into PNG; original font is unknown,
visually resembles Times New Roman. Adapt with20-22px Times New Roman text,
black background, >=8px margins. Source SVG has independent text objects but
Photoshop can rasterize it on import; use Photoshop text layers for editing.
No replacement controls image installed yet.

Validation: actual word-wrapper tested on full two-key text and red cleaver;
animation reference and actual route tests passed; C syntax with PSP stubs,
shell syntax, font assets and same-length dialogue colour edit checks.
PSP SDK/emulator runtime unavailable here.

Install (close PPSSPP):
cd ~/projects/naraku-psp
unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_0.8.5_text_motion_patch.zip
chmod +x tools/build_deploy_v085.sh
./tools/build_deploy_v085.sh
