# NARAKU PSP

An unofficial, work-in-progress PSP port of **Purgatory -NARAKU-**.

**Current version: 1.3.3 · Development build · Source repository**

## Current progress

The current implementation covers **Maps 001–045**, including the opening, early puzzles, flashbacks, chase sequences and the factory section through the crank/lift puzzle and password terminals.

**Maps 046 onward are outside the completed implementation scope.** A complete playthrough across all branches and endings is not yet supported and verified. Implemented content may still contain bugs.

## Implemented features

- Movement, running, object interaction and item collection.
- Dialogue, choices, animated dialogue windows and colored item names.
- Inventory, key items and notes, with a translucent menu over the current scene.
- In-game saving and loading.
- Story events, flashbacks and chase behavior in the implemented sections.
- Lasers, traps and their associated death sequences.
- Music and sound effects for the implemented events.
- Factory mechanisms, metal-sheet interactions, key collection and password input.

## Latest changes

Version **1.3.3** restores the original capitalization of English item names while retaining their added color emphasis. All 1.3.2 changes are retained, including:

- Rebuilt character portraits and expressions for 66 dialogue picture assets.
- Corrected action-event selection for metal-sheet interactions.
- Revised corridor texture sampling intended to reduce movement shimmer; final appearance needs gameplay testing.

See [the 1.3.3 release notes](docs/releases/1.3.3.md).

## Repository contents

| Path | Purpose |
| --- | --- |
| `main.c` | Game loop, rendering and event execution |
| `runtime/` | Extracted gameplay components |
| `tools/` | Asset preparation, build and deployment scripts |
| `tests/` | Host-side logic, text and asset-conversion checks |

Original and converted game assets, music, XMB artwork, saves and compiled builds are **not included**. Local assets are required to run the game. Asset preparation tools are provided, but a verified end-to-end procedure for rebuilding every required asset from scratch is not yet available. The current testing workflow requires an existing complete local port installation.

## Building

Install PSPDEV/PSPSDK, CMake and Make. From the repository root:

```bash
mkdir -p build
cd build
psp-cmake ..
make -j"$(nproc)"
```

Output: `build/EBOOT.PBP`. Local `xmb/ICON0.PNG`, `xmb/PIC1.PNG` and `xmb/SND0.AT3` files are used when present.

To build and deploy 1.3.3 over a complete local installation, with the prepared `assets/` directory available:

```bash
chmod +x tools/build_deploy_v133.sh
./tools/build_deploy_v133.sh /path/to/PSP/GAME/NARAKU
```

Close PPSSPP before replacing `EBOOT.PBP`. Fully restart the game after updating and load an **in-game save**. Emulator save states from older builds can restore the previous executable.

## Testing

Install Python dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Some tests require a host C compiler, original game data, local `assets/` and earlier patch archives. The suite is not self-contained without these files. Host-side checks do not replace PPSSPP or real PSP gameplay testing. Comprehensive real-hardware compatibility has not been verified for this development build.

## Controls

| Button | Action |
| --- | --- |
| D-pad | Move / select |
| X | Interact / confirm |
| O | Cancel / open menu / advance dialogue |
| R + direction | Run |
| L / R | Menu tabs and pages |
| Hold Select at launch | Language selection |

## Credits and licensing

This is an independent fan project. The original game's title, characters, artwork, music and data belong to their respective rights holders.

A source-code license has not yet been selected. Availability of this repository does not grant permission to redistribute the original game's assets.
