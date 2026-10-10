NARAKU PSP 1.7.7 — Russian language (test build)

Adds Russian as a fifth selectable language alongside English, Japanese,
Simplified Chinese and Traditional Chinese. Select Settings > Language >
Русский. The selection persists in config.bin; existing save slots work.

Translated content:
- Enri and Will dialogue, choices, all endings, secret/bonus area and credits.
- Item and key-item names/descriptions, title/options/save/load prompts.
- Delete-save confirmation and results, and a separate PSP controls card.
- 1,834 unique source fragments, assembled into 2,339 lookup entries.

This is an unofficial Russian translation made for the PSP port. It is
ready for tester review, not claimed to have undergone a full Russian
playthrough. Report awkward wording or layout with a screenshot and map/scene.
Names, in-universe brands, puzzle codes and artwork labels are retained where
appropriate; image illustrations and the game logo are not repainted.

Preservation:
Russian uses a separate ~236 KiB dictionary and an additional 256 KiB Cyrillic
font atlas. The four existing dialogue/UI variants, old glyphs and game scripts
are not translated or regenerated. Original controls remain for other languages.
Colour emphasis and auto-close controls are preserved. Russian prose wraps by
words and paginates instead of dropping overflow; ending captions keep authored
lines. No progress/config deletion occurs during installation.

Install over the current project:
  unzip -t /mnt/c/Users/Rgood/Downloads/naraku_psp_1.7.7_russian_patch.zip
  unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.7.7_russian_patch.zip
  chmod +x tools/build_deploy_v177.sh
  ./tools/build_deploy_v177.sh
Restart PPSSPP/the game, then load an in-game save. Do not restore a savestate
created with an older executable to test this patch.
The patch contains source/resources, not a precompiled EBOOT or full game.

Checks performed:
- Actual C dictionary lookup tested against 1,272 distinct source/ported/UI
  strings. All dialogue strings compiled from 139 original maps are covered.
- 1,834 translation records complete; source auto-close controls retained.
- Cyrillic coverage and unchanged old font pages/glyphs checked.
- Existing map/common-event binaries compared byte-for-byte with 1.7.6.
- Host C syntax and deployment shell syntax checked.
No real PSP/PPSSPP rendering or full Russian playthrough was performed here.

Editing the translation:
  tools/ru_source.json: indexed unique English fragments.
  tools/ru_translation.tsv: index + tab + Russian (literal \n = authored newline).
  tools/prepare_russian_v177.py ORIGINAL_GAME_FOLDER
  tools/pack_russian_v177.py
Keep the old-language resources; these scripts only build the additive dictionary
and append Russian glyphs. They require Python/Pillow and DejaVu Sans Mono fonts.
