NARAKU PSP 0.9.2 — original inventory opacity
Original js/rmmz_scenes.js Scene_MenuBase: background opacity 192/255.
Original data/System.json advanced.windowOpacity: 192.
Original js/plugins.js OptionEx defaultWindowOpacity: 195.
Original OptionEx.js precedence: saved config, System advanced, plugin fallback.
Port inventory now uses background alpha 192 and existing window-opacity setting
(default 195), instead of hardcoded alpha 100. Saved preferences preserved.
Lighter 0.9.1 blur and working current-world readback preserved.
Install over full game with tools/build_deploy_v092.sh.
Host regression/C syntax checks; PSP runtime not available.
