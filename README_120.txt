NARAKU PSP 1.2.0 cumulative patch

S-003: preserve original 72x144 RGBA frames, three walking patterns/four directions packed in two direction columns and two rows. Runtime draws at PSP half scale. Restore chase secondary-axis fallback at blocked walls; clear skipped movement deltas.
Gold key: sentence-aware lowercase and gold color palette 14. Red/iron/green keys keep their prior fixes. Trailing RPG Maker controls never render as text.
Actual CPU dialogue rasterizer tested with the four reported messages: shutter and first Emma message two rows; materials/heavy messages three rows with no lost glyphs.
Force rebuild EBOOT. Exclude PNG previews from deploy. All previous changes included.

IMPORTANT: after updating EBOOT, completely stop and relaunch the game. Load with the game Load menu. Old PPSSPP save states restore RAM and executable code; they cannot be migrated by replacing EBOOT. New-version state restoration is not runtime-tested here.
Host regression tests passed; PSP build/PPSSPP runtime unavailable.

cd ~/projects/naraku-psp
unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_1.2.0_chase_text_sprite_patch.zip
chmod +x tools/build_deploy_v120.sh
./tools/build_deploy_v120.sh
