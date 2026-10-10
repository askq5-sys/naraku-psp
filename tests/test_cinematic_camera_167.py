"""Execute the actual camera and check original underground scrolling payload."""
from pathlib import Path
import subprocess,tempfile,sys,struct
r=Path(__file__).resolve().parents[1];s=(r/'main.c').read_text()
a=s.index('static void compute_camera(');b=s.index('static void draw_map_slot_local',a)
pre='''#include <assert.h>
#define TILE_PX 24
#define SCREEN_W 480
#define SCREEN_H 272
typedef struct{int id,w,h;}MapState;
static int g_camera_locked;
static float g_camera_lock_x,g_camera_lock_y,g_camera_scroll_x,g_camera_scroll_y;
static float clamp_float(float x,float lo,float hi){return x<lo?lo:x>hi?hi:x;}
'''
post='''int main(void){float cx,cy,ox,oy;MapState m={98,18,25};
g_camera_scroll_y=-240;compute_camera(&m,12,600,&cx,&cy,&ox,&oy);
assert(ox+13.5f*24-cx==264);assert(cy==144);assert(6*24-cy==0);assert(240-cy-39>=24&&240-cy<210);
m=(MapState){99,20,13};g_camera_scroll_y=0;compute_camera(&m,480,216,&cx,&cy,&ox,&oy);
assert(ox+15.5f*24-cx==240);assert(ox+18.5f*24-cx<480);
m=(MapState){82,30,20};compute_camera(&m,400,240,&cx,&cy,&ox,&oy);assert(ox==0&&cx==160);
return 0;}'''
with tempfile.TemporaryDirectory()as td:
 p=Path(td)/'t.c';e=Path(td)/'t';p.write_text(pre+s[a:b]+post)
 subprocess.run(['cc','-std=c99',str(p),'-o',str(e)],check=True);subprocess.run([str(e)],check=True)
sys.path.insert(0,str(r/'tools'));import prepare_world_v060 as w
G=r.parent/'original';texts=w.read_json(G/'data/I18NTexts.json');mp=w.read_json(G/'data/Map104.json')
commands=mp['events'][2]['pages'][0]['list'];at=next(i for i,c in enumerate(commands)if c['code']==105)
chunk=[]
for c in commands[at:]:
 if chunk and c['code']!=405:break
 chunk.append(c)
payload=w.compile_vm_commands({'list':chunk},texts)
assert payload[:3]==bytes([43,1,0]);lens=struct.unpack_from('<4H',payload,3);off=11
for lk,n in zip(w.LANG_KEYS,lens):
 value=payload[off:off+n].decode();off+=n
 assert value=='\n'.join(w.localized_string(c['parameters'][0],texts,lk)for c in chunk[1:])
assert off==len(payload)-1 and len(chunk)==32
print('PASS: actual cinematic camera keeps the main shot visible; city camera unchanged; all 31 original epilogue lines retained in four languages')
