NARAKU PSP 0.8.9 — world framebuffer inventory capture
Reads the last completed GU world framebuffer directly via uncached VRAM.
Does not depend on display-API framebuffer state. VRAM offset zero is valid.
Captures before menu common event, refreshes every opening, blurs current location.
Includes all prior font, animation and inventory assets and fixes.
Install over full game using tools/build_deploy_v089.sh.
Validation: host animation/routes and C syntax. No PSP/PPSSPP runtime here.
