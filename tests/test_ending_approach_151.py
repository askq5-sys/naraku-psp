from pathlib import Path
import struct,subprocess,sys,tempfile
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'tools'));import prepare_world_v060 as w
original=w.read_json(r.parent/'original/data/Map078.json');data=w.adapt_stage_151(original,78)
assert original['events'][2]['y']==10
assert w.adapt_stage_151(data,78)==data
texts=w.read_json(r.parent/'original/data/I18NTexts.json');O=r/'assets';w.PICTURE_IDS=w.read_json(O/'picture_v050_manifest.json')
rows=w.read_json(O/'audio_exact_v079.json');w.EXACT_SE_IDS={w.audio_key(x):x['id']for x in rows if x['kind']=='se'};w.EXACT_BGM_IDS={w.audio_key(x):x['id']for x in rows if x['kind']=='bgm'}
raw=(O/'map078_vm.bin').read_bytes();ne=struct.unpack_from('<H',raw,4)[0];pb=20+ne*10;blob=struct.unpack_from('<I',raw,8)[0]
for eid in (2,8,9,10):
 ev=data['events'][eid];old=original['events'][eid]['pages'][0]['list'];new=ev['pages'][0]['list'];dx=7-ev['x']
 assert ev['y']==9
 if dx:
  align=new[0]['parameters'][1];assert align['wait'] and not align['repeat']
  codes=[c['code']for c in align['list']if c['code']];assert codes==[3 if dx>0 else 2]*abs(dx)
  assert ev['x']+sum(1 if c==3 else -1 for c in codes)==7
  assert new[1:]==old[2:]
 else:assert new==old[2:]
 assert not any(c['code']==201 and c['parameters'][1]==78 for c in new)
 for i in range(ne):
  e,x,y,first,n,_=struct.unpack_from('<HHHHBB',raw,20+i*10)
  if e==eid:
   assert (x,y)==(ev['x'],9)
   off,size=struct.unpack_from('<II',raw,pb+20*first+12)
   assert raw[blob+off:blob+off+size]==w.compile_vm_commands(ev['pages'][0],texts,True)
for ev in original['events']:
 if ev and ev['id']not in(2,8,9,10):assert data['events'][ev['id']]==ev
# Compile the actual margin drawing block and verify its scope and fade.
s=(r/'main.c').read_text();a=s.index('        if (p->resource_id==104 && p->fit_screen)');b=s.index('        if (!p->portrait',a)
code=r'''#include <assert.h>
#define GU_ADD 0
#define GU_SRC_ALPHA 0
#define GU_ONE_MINUS_SRC_ALPHA 0
#define SCREEN_W 480
#define SCREEN_H 272
typedef struct{int resource_id,fit_screen,opacity;}Picture;
static int calls;static float positions[2],widths[2];static int alphas[2];
static void sceGuBlendFunc(int a,int b,int c,int d,int e){}
static void draw_solid_rect(float x,float y,float w,float h,int r,int g,int b,int a){assert(y==0&&h==272&&r==255&&g==255&&b==255);positions[calls]=x;widths[calls]=w;alphas[calls++]=a;}
static void draw(int id,int opacity){Picture value={id,1,opacity},*p=&value;float w=408.f*272/312,x=(480-w)/2;
'''+s[a:b]+r'''}
int main(void){for(int a=1;a<=255;a++){calls=0;draw(104,a);assert(calls==1&&positions[0]==0&&widths[0]==480&&alphas[0]==a);}for(int id=90;id<110;id++)if(id!=104){calls=0;draw(id,255);assert(!calls);}return 0;}'''
with tempfile.TemporaryDirectory()as td:
 p=Path(td)/'t.c';e=Path(td)/'t';p.write_text(code);subprocess.run(['cc','-std=c99',str(p),'-o',str(e)],check=True);subprocess.run([str(e)],check=True)
print('PASS: all four entrances walk to alignment without a same-map warp, scene tails preserved, packed VM updated; white side fields only on Finish A1 at all fade levels')
