from pathlib import Path
import subprocess,tempfile
r=Path(__file__).resolve().parents[1]
s=(r/'main.c').read_text();a=s.index('static void draw_runtime_message_overlay(void)');b=s.index('static void render_picture_frame(',a)
pre="""#include <assert.h>
#include <stddef.h>
#define MESSAGE_BOX_X 110
#define MESSAGE_BOX_Y 210
#define MESSAGE_BOX_W 260
#define MESSAGE_BOX_H 62
#define MESSAGE_NAME_H 26
#define MESSAGE_SURFACE_W 512
#define MESSAGE_SURFACE_H 256
#define MESSAGE_SURFACE_X 0
#define MESSAGE_SURFACE_Y 192
#define MESSAGE_SURFACE_SCALE 2
#define GU_TFX_REPLACE 0
#define GU_TCC_RGBA 0
#define GU_LINEAR 0
#define GU_NEAREST 0
static int g_runtime_message_active=1,g_runtime_message_openness=255,g_window_opacity=255;
static int g_runtime_message_transparent,g_runtime_message_surface_ready,frames,texts;
static void *g_runtime_message_surface;
static const char *g_runtime_speaker,*g_runtime_message="END 1/7 No Salvation";
static size_t g_runtime_speaker_len,g_runtime_message_len=20;
static int runtime_speaker_width(void){return 60;}
static int runtime_message_text_y(void){return 218;}
static void draw_message_window_reveal(float x,float y,float w,float h,int a){frames++;}
static void bind_texture_8888(){}
static void sceGuTexFunc(){}
static void sceGuTexFilter(){}
static void sceGuColor(){}
static void draw_bound_rect(){texts++;}
static void draw_utf8_wrapped(){texts++;}
"""
post="""int main(void){
g_runtime_message_transparent=1;draw_runtime_message_overlay();assert(frames==0&&texts==1);
frames=texts=0;g_runtime_message_transparent=0;draw_runtime_message_overlay();assert(frames==1&&texts==1);
frames=texts=0;g_runtime_speaker="Enri";g_runtime_speaker_len=4;draw_runtime_message_overlay();assert(frames==2&&texts==2);
frames=texts=0;g_runtime_message_transparent=1;g_runtime_message_surface_ready=1;g_runtime_message_surface=(void*)1;draw_runtime_message_overlay();assert(frames==0&&texts==1);
return 0;}
"""
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(pre+s[a:b]+post)
 subprocess.run(['cc',str(p/'test.c'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
print('PASS: transparent cached/fallback text without frames, normal dialogue and speaker frames retained')
