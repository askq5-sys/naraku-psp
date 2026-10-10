NARAKU PSP 0.9.4 — native inventory icons and shutter text
Original IconSet is 512x640; old conversion resized it and broke 32px cell UVs.
Rebuilt 512x512 atlas by cropping native cells, preserving original RGBA colors.
All inventory item icon indices are below 256, including notes at index 176.
English shutter message hard newline replaced by a same-size space in VM assets;
automatic wrapping can use two lines. Other languages and offsets preserved.
Install over full game using tools/build_deploy_v094.sh.
Host route/animation and C syntax checks; emulator visual check still needed.
