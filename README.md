# Purgatory -NARAKU- PSP

An unofficial PSP homebrew port of Purgatory -NARAKU-.

## Current version: 1.7.8

The port implements Enri's and Will's stories, the ending routes,
secret-route events, and bonus areas. The developer has completed
the available routes during testing; broader hardware and regression
testing is still needed.

This is a test release. Implemented content should not be interpreted
as a guarantee that every branch is free of bugs.

## Features

- Enri and Will, with character-aware save-slot previews.
- Dialogue, choices, scripted movement, chases and puzzles.
- Inventory, key items, notes, save/load and settings menus.
- Normal, dimmed and transparent message windows.
- Original music and sound effects.
- English, Japanese, Simplified Chinese and Traditional Chinese.
- An additional unofficial Russian translation.
- Save-file deletion with confirmation in all five languages.
- Settings values aligned to a shared right edge.

## Changes in 1.7.7–1.7.8

- Added Russian dialogue, choices, item descriptions, menus,
  ending captions and credits.
- Added Cyrillic glyphs and a separate Russian PSP controls card.
- Preserved the four existing language variants and prior script fixes.
- Added Russian word wrapping and pagination for dialogue.
- Aligned language, ON/OFF and numeric settings values to the right.

The Russian translation is ready for tester review.
Its wording and layout have not undergone a complete Russian playthrough.

## Controls

| Button | Action |
| --- | --- |
| D-pad | Move |
| X | Confirm / interact / examine |
| O | Open menu / cancel |
| R | Dash |

## Installation

The release attachment is an incremental source/resource patch,
not a standalone game or a precompiled EBOOT.

Apply it over an existing port project:

```bash
cd ~/projects/naraku-psp
unzip -t /path/to/naraku_psp_1.7.8_settings_alignment_patch.zip
unzip -o /path/to/naraku_psp_1.7.8_settings_alignment_patch.zip
chmod +x tools/build_deploy_v178.sh
./tools/build_deploy_v178.sh
```

Building requires a working PSP SDK environment.
The deployment script accepts an optional destination directory.
Restart the game after updating and load an in-game save.
Avoid using emulator savestates created with an older executable.
Select Russian through Settings → Language → Русский.
Bug reports
Submit a bug report with screenshots or video
Please include:
- Port version and selected language.
- PSP model and firmware, or PPSSPP version and platform.
- Location, story route and steps to reproduce.
- Expected behaviour and what happened instead.
- Whether you loaded an in-game save or an emulator savestate.
- Screenshots or a short video, where possible.
Validation
Host checks cover translation lookup, Cyrillic coverage, preservation
of existing dialogue/script resources, and selected runtime regressions.
Real PSP compatibility, visual layout and complete route coverage
still require tester verification.
Credits
Original game: Nama.
This is an unofficial fan port and is not affiliated with the original
creator. Original game assets remain the property of their respective owners.

## Bug reports

[Submit a bug report with screenshots or video](https://docs.google.com/forms/d/e/1FAIpQLSeCmy7igU36vjf8h_UQxBvWXnwr3AmQDEiRwXMiN3tbJ9G-bg/viewform)

Include the port version, language, location, steps to reproduce, expected
and actual behaviour, and whether you loaded an in-game save or savestate.
