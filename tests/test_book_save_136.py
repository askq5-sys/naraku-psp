"""Run the real slot UI with disabled menu saving and a held opening button."""
from pathlib import Path
import re,subprocess,tempfile
r=Path(__file__).resolve().parents[1];s=(r/'main.c').read_text()
a=s.index('static int ui_save_load_scene(');b=s.index('static const char *title_path_for_language',a)
pre=r'''#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
typedef struct{uint32_t Buttons;}SceCtrlData;
typedef struct{int unused;}ProgressState;
static int g_save_enabled,g_language,frames,reads,saved,cancel;
static void *g_ui_char_atlas;
#define SAVE_SLOT_COUNT 20
#define PSP_CTRL_UP 4
#define PSP_CTRL_DOWN 8
#define PSP_CTRL_LTRIGGER 16
#define PSP_CTRL_RTRIGGER 32
#define UI_L_SAVE_PROMPT 1
#define UI_L_LOAD_PROMPT 2
#define UI_L_FILE 3
#define CHAR_ATLAS_W 512
#define CHAR_ATLAS_H 512
#define CHAR_SLOT_W 48
#define CHAR_SRC_W 48
#define CHAR_SRC_H 96
#define GU_LINEAR 1
#define SE_UI_CURSOR_PATH "cursor"
#define SE_UI_SAVE_PATH "save"
#define SE_UI_LOAD_PATH "load"
#define SE_UI_BUZZER_PATH "buzz"
#define SE_UI_CANCEL_PATH "cancel"
#define ui_draw_save_background(...) ((void)0)
#define draw_naraku_window(...) ((void)0)
#define ui_inventory_name(...) ((void)0)
#define draw_solid_rect(...) ((void)0)
#define bind_texture_8888(...) ((void)0)
#define set_pixel_art_texture_state(...) ((void)0)
#define sceGuTexFilter(...) ((void)0)
#define draw_bound_rect(...) ((void)0)
#define ui_format_playtime(...) ((void)0)
#define play_se_async(...) ((void)0)
static void ui_frame_begin(void){assert(++frames<5);}
static void ui_frame_end(void){}
static int ui_label_text(int k,int l,const char **p,size_t *n){return 0;}
static int save_slot_metadata(int slot,int *m,int *x,int *y,uint32_t*t){return 0;}
static int save_slot_exists(int slot){return 0;}
static int load_from_slot(int slot,ProgressState*p){return 0;}
static uint32_t ui_ok_mask(void){return 1;}
static uint32_t ui_cancel_mask(void){return 2;}
static void sceCtrlPeekBufferPositive(SceCtrlData*p,int n){p->Buttons=reads==0?1:reads==1?0:cancel?2:1;++reads;}
static int save_to_slot(int slot,int map,int x,int y,int dir){assert(frames==2&&slot==1&&map==57&&x==9&&y==5&&dir==2);++saved;return 1;}
'''
post='''int main(void){assert(!g_save_enabled);assert(ui_save_load_scene(1,57,9,5,2,NULL)==1&&saved==1&&frames==2);frames=reads=0;cancel=1;assert(ui_save_load_scene(1,57,9,5,2,NULL)==0&&saved==1&&frames==2);return 0;}'''
with tempfile.TemporaryDirectory()as tmp:
 p=Path(tmp)/'save.c';exe=Path(tmp)/'save';p.write_text(pre+s[a:b]+post)
 subprocess.run(['cc','-std=c99',str(p),'-o',str(exe)],check=True);subprocess.run([str(exe)],check=True)
print('PASS: direct book Save opens with menu saving disabled, release arms confirmation, current coordinates saved, cancellation does not save')
