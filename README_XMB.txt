NARAKU PSP — XMB artwork and title-menu music

Apply over your existing 0.7.9 project:
  cd ~/projects/naraku-psp
  unzip -o /mnt/c/Users/Rgood/Downloads/naraku_psp_xmb_patch.zip
  chmod +x tools/build_deploy_xmb.sh
  ./tools/build_deploy_xmb.sh

The complete game must already be deployed. This script rebuilds only EBOOT.PBP
in build_xmb and copies it to your PPSSPP game folder. Assets and saves remain.
The regular build_deploy_v079.sh will also embed this artwork after applying
this patch, because CMakeLists.txt includes the XMB resources.

ICON0.PNG: supplied header.jpg, fitted without distortion to 144x80.
PIC1.PNG: original System.json title1Name background, fitted to 480x272 without
stretching or trimming the artwork. Narrow black sidebars preserve its proportions.
SND0.AT3: original System.json titleBgm, first 20 seconds at original volume 50,
with 0.4-second fade-in and 1-second fade-out. ATRAC3, stereo, 44100 Hz,
331468 bytes. Source game: the supplied original NARAKU copy.
No trailer/video is included in this static artwork patch.

Checks: PNG files inspected at target sizes; ATRAC decoded fully by FFmpeg;
CMake parameter names checked against official PSPSDK CreatePBP.cmake;
build/deploy script passed shell syntax checks.
PSP linking and XMB playback have not been tested in this environment.

Artwork is embedded into EBOOT.PBP; the xmb source folder does not need to be
copied onto the PSP separately. When sharing, send the normal complete NARAKU
folder containing EBOOT.PBP and assets. Folder name must remain NARAKU.

Encoding tool: https://github.com/dcherednik/atracdenc (cb17070), not included.
Packaging reference:
https://github.com/pspdev/pspsdk/blob/master/src/base/CreatePBP.cmake
