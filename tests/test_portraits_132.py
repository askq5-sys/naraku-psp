from pathlib import Path
import json,struct,sys,subprocess,tempfile
import numpy as np
from PIL import Image
r=Path(__file__).resolve().parents[1];O=r/'assets';G=r.parent/'original';sys.path.insert(0,str(r/'tools'));import prepare_world_v060 as w
key=bytes.fromhex(json.load(open(G/'data/System.json'))['encryptionKey']);rows=json.load(open(O/'portraits_v132.json'))
for row in rows:
 b=(O/f'pic_{row["id"]:03}.p44').read_bytes();header=struct.unpack_from('<4s8H',b);magic,tw,th,cw,ch,x,y,bw,bh=header
 assert magic==b'NPR1'and len(b)==20+512*512*2 and(tw,th)==tuple(row['texture_region'])and(cw,ch)==tuple(row['logical'])
 src=w.load_encrypted_png(w.resolve_named_file(G/'img/pictures',row['name']),key);crop=src.crop(row['bounds']).resize((tw,th),Image.Resampling.LANCZOS)
 a=np.asarray(crop,dtype=np.uint16)>>4;expected=a[:,:,0]|a[:,:,1]<<4|a[:,:,2]<<8|a[:,:,3]<<12;packed=np.frombuffer(b[20:],dtype='<u2').reshape(512,512)
 assert np.array_equal(packed[1:th+1,1:tw+1],expected)
 assert not packed[0].any()and not packed[:,0].any();assert tw>=bw*.5 and th>=bh*.5
 assert [x,y,x+bw,y+bh]==row['bounds']and(cw,ch)==tuple(round(v*.5)for v in src.size)
# Exercise actual loader and draw routine for the new format and legacy pictures.
s=(r/'main.c').read_text();a=s.index('#define MAX_ACTIVE_PICTURES');b=s.index('static volatile int g_audio_stop',a);types=s[a:b]
a=s.index('static PictureSlot *picture_slot(');b=s.index('static void draw_fog_a1_overlay(',a);loader=s[a:b]
a=s.index('static void draw_vm_pictures(');b=s.index('static void draw_lucas_fall_event(',a);drawing=s[a:b]
pre='''#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <math.h>
#define SCREEN_W 480
#define SCREEN_H 272
#define GU_PSM_4444 1
#define GU_FALSE 0
#define GU_TFX_MODULATE 2
#define GU_TFX_REPLACE 3
#define GU_TCC_RGBA 4
#define GU_LINEAR 5
#define GU_NEAREST 6
#define GU_ADD 7
#define GU_SRC_ALPHA 8
#define GU_FIX 9
#define GU_DST_COLOR 10
#define GU_ONE_MINUS_SRC_ALPHA 11
#define GU_ONE_MINUS_SRC_COLOR 12
static int g_picture6_alpha,g_picture6_visible;static unsigned char g_switches[1601];
static float ux,uy,uw,uh,dx,dy,dw,dh;static int filter,draws;
static uint16_t read_u16_le(const unsigned char*p){return p[0]|p[1]<<8;}
static void*memalign(int a,size_t n){return malloc(n);}
static void sceKernelDcacheWritebackInvalidateAll(void){}
static float render_round_pixel(float x){return floorf(x+.5f);}
static void sceGuTexMode(int a,int b,int c,int d){}
static void sceGuTexImage(int a,int b,int c,int d,void*p){}
static void sceGuTexFunc(int a,int b){}
static void sceGuTexFilter(int a,int b){filter=a;}
static void sceGuBlendFunc(int a,int b,int c,int d,int e){}
static void sceGuColor(unsigned int a){}
static void draw_bound_rect(float x,float y,float w,float h,float xx,float yy,float ww,float hh){ux=x;uy=y;uw=w;uh=h;dx=xx;dy=yy;dw=ww;dh=hh;draws++;}
'''+ '#define ASSET_ROOT '+json.dumps(str(O.resolve())+'/')+'\n'
post='''int main(void){picture_show(8,18,0,0,0,100,100,255);PictureSlot*p=picture_slot(8);assert(p&&p->texture&&p->portrait&&p->w==408&&p->h==312&&!p->fit_screen);
draw_vm_pictures(0);assert(filter==GU_LINEAR&&ux==1&&uy==1&&uw==p->source_w&&uh==p->source_h);assert(dx==36+p->picture_offset_x&&dy==-20+p->picture_offset_y&&dw==p->picture_region_w&&dh==p->picture_region_h);
p->number=11;p->origin=1;p->scale_x=p->scale_y=50;draw_vm_pictures(0);assert(dw==p->picture_region_w*.5f&&dh==p->picture_region_h*.5f);assert(dx==36-102+p->picture_offset_x*.5f&&dy==-20-78+p->picture_offset_y*.5f);erase_picture_slot(11);
picture_show(8,93,0,0,0,100,100,255);p=picture_slot(8);assert(p->texture&&!p->portrait&&p->fit_screen);draw_vm_pictures(0);assert(dx==0&&dy==0&&dw==480&&dh==272&&ux==0);erase_picture_slot(8);return 0;}'''
with tempfile.TemporaryDirectory()as td:
 p=Path(td)/'t.c';e=Path(td)/'t';p.write_text(pre+types+loader+drawing+post);subprocess.run(['cc','-std=c99',str(p),'-lm','-o',str(e)],check=True);subprocess.run([str(e)],check=True)
print(f'PASS: {len(rows)} portrait alpha crops/native texels/geometry; actual new/legacy picture loader, linear draw, origin/zoom and game-over fitting; fixed 512KiB texture memory')
