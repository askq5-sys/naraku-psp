NARAKU PSP 0.8.1 — title menu patch (requires existing full game assets)
Hold Up/Down: repeat after 400 ms, then every 100 ms; stops at the edge.
Release and press again at an edge to wrap. No cursor sound when blocked.
Title frame: thin red border with black edges, dark rows, burgundy selection,
centered labels. Current PSP dimensions retained for readable text.
Gameplay, saves, assets and XMB configuration preserved.

WSL installation:
cd ~/projects/naraku-psp
unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_0.8.1_menu_patch.zip
chmod +x tools/build_deploy_v081.sh
./tools/build_deploy_v081.sh

Validated: C syntax with PSP stubs, host navigation behavior tests, shell syntax.
Real PSP compilation and device testing require your PSP SDK/hardware.
