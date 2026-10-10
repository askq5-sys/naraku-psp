"""Exercise the actual picture renderer with a password note and a portrait."""
from pathlib import Path
import re,subprocess,tempfile
r=Path(__file__).resolve().parents[1];s=(r/'main.c').read_text();a=s.index('static void draw_vm_pictures(');b=s.index('static int lucas_fall_frame_from_switches',a)
pre=r'''#include <assert.h>
#include <stddef.h>
#define SCREEN_W 480
#define SCREEN_H 272
#define MAX_ACTIVE_PICTURES 4
typedef struct{int number,resource_id,w,h,portrait,fit_screen,origin,blend;float opacity,scale_x,scale_y,x,y,source_w,source_h,picture_offset_x,picture_offset_y,picture_region_w,picture_region_h;void*texture;}PictureSlot;
static PictureSlot g_pictures[4];static int masked,drawn,sequence;
static float render_round_pixel(float v){return (int)(v+0.5f);}
static void draw_solid_rect(float x,float y,float w,float h,int r,int g,int b,int a){assert(x==0&&y==0&&w==480&&h==272&&!r&&!g&&!b&&a==255);assert(sequence++==0);++masked;}
static void draw_bound_rect(float a,float b,float c,float d,float x,float y,float w,float h){assert(sequence++>=0);++drawn;}
'''
for fn in ['sceGuTexMode','sceGuTexImage','sceGuTexFunc','sceGuTexFilter','sceGuBlendFunc','sceGuColor']:pre+=f'#define {fn}(...) ((void)0)\n'
for name in set(re.findall(r'\bGU_[A-Z0-9_]+',s[a:b])):pre+=f'#define {name} 0\n'
post=r'''int main(void){g_pictures[0]=(PictureSlot){.number=60,.resource_id=101,.w=408,.h=312,.opacity=255,.scale_x=100,.scale_y=100,.texture=(void*)1};draw_vm_pictures(0);assert(masked==1&&drawn==1&&sequence==2);sequence=masked=drawn=0;g_pictures[0].portrait=1;g_pictures[0].resource_id=40;draw_vm_pictures(0);assert(masked==0&&drawn==1);g_pictures[0].opacity=0;draw_vm_pictures(0);assert(masked==0&&drawn==1);return 0;}'''
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp)/'note.c';e=Path(tmp)/'note';p.write_text(pre+s[a:b]+post);subprocess.run(['cc','-std=c99',str(p),'-o',str(e)],check=True);subprocess.run([str(e)],check=True)
print('PASS: C=5762 note masks the entire viewport before its picture; portraits and erased notes do not mask gameplay')
