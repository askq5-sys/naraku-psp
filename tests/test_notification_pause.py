from pathlib import Path
import subprocess,tempfile
r=Path(__file__).resolve().parents[1];s=(r/'main.c').read_text();a=s.index('static char *style_green_key_dialogue(');b=s.index('/* Reflow the PC-authored',a)
pre=r'''#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
#define PSP_CTRL_CROSS 1
#define PSP_CTRL_CIRCLE 2
typedef struct {int id;} MapState;
typedef struct {uint32_t Buttons;} SceCtrlData;
static int g_language,g_runtime_message_active,g_runtime_message_surface_ready,g_runtime_message_openness;
static const char*g_runtime_speaker,*g_runtime_message;
static size_t g_runtime_speaker_len,g_runtime_message_len;
static int frames,rebuilt;
static int latin_word_cp(unsigned c){return (c>='a'&&c<='z')||(c>='A'&&c<='Z');}
static int parse_text_color_escape(const char**p,const char*end,int*color){return 0;}
static int vm_text_has_visible_content(const char*p,size_t n){return p&&n;}
static void rebuild_runtime_message_surface(void){const char*t="Obtained an Iron Key.";assert(g_runtime_message_len==strlen(t)&&!memcmp(g_runtime_message,t,strlen(t)));rebuilt++;}
static void vm_render_frame(const MapState*m,void*a,int x,int y,int d,int z,int q){assert(++frames<100);}
static void sceCtrlPeekBufferPositive(SceCtrlData*p,int n){p->Buttons=0;}
'''
import json
message="Obtained an Iron Key."+chr(92)+"^"+chr(10)
post='int main(void){MapState m={24};const char*t='+json.dumps(message)+';vm_wait_text_page(&m,NULL,0,0,0,"",0,t,strlen(t),0);assert(rebuilt==1&&frames==46&&!g_runtime_message_active&&!g_runtime_message_openness);return 0;}'
with tempfile.TemporaryDirectory()as tmp:
 p=Path(tmp)/'t.c';e=Path(tmp)/'t';p.write_text(pre+s[a:b]+post);subprocess.run(['cc',str(p),'-o',str(e)],check=True);subprocess.run([str(e)],check=True)
print('PASS: original Iron Key notification preserves original case without control codes, advances with no input, and closes its window')
