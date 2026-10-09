from pathlib import Path
import json,struct,subprocess,tempfile
root=Path(__file__).resolve().parents[1];s=(root/'main.c').read_text();a=s.index('static void tick_pressing_room(');b=s.index('/* Map032 parallel pages',a)
pre='''#include <assert.h>
#include "runtime/pressing_room.h"
typedef struct {int id;} MapState;
static int g_pressing_room_frame,se,flash;
static unsigned char g_switches[1601];
static void vm_begin_screen_flash(int r,int g,int b,int alpha,int frames){assert(r==255&&g==0&&b==0&&alpha==255&&frames==5);flash++;}
static void play_vm_se_params(int id,int v,int p,int pan){assert(id==1133&&v==90&&p==100&&pan==0);se++;}
'''
post='''int main(void){MapState m={24};
for(int cycle=0;cycle<2;cycle++){for(int t=1;t<=220;t++){tick_pressing_room(&m);if(t==60)assert(g_switches[183]&&!g_switches[184]);if(t==120)assert(!g_switches[183]&&g_switches[184]&&se==cycle+1);if(t==220)assert(!g_switches[183]&&!g_switches[184]&&g_pressing_room_frame==0);}}
assert(se==2&&flash==2);for(int t=0;t<50;t++)tick_pressing_room(&m);g_switches[191]=1;tick_pressing_room(&m);assert(g_pressing_room_frame==0&&se==2);g_switches[191]=0;m.id=14;tick_pressing_room(&m);assert(se==2&&g_pressing_room_frame==0);return 0;}
'''
with tempfile.TemporaryDirectory()as tmp:
 p=Path(tmp)/'t.c';exe=Path(tmp)/'t';p.write_text(pre+s[a:b]+post);subprocess.run(['cc','-I',str(root),str(p),'-o',str(exe)],check=True);subprocess.run([str(exe)],check=True)
rows=json.load(open(root/'assets/audio_exact_v079.json'));ids={(x['name'],x['volume'],x['pitch'],x['pan']):x['id']for x in rows if x['kind']=='se'}
for mid,eid,pi in [(24,3,5),(25,3,1),(27,2,0)]:
 original=json.load(open(root.parent/('original/data/Map%03d.json'%mid)))['events'][eid]['pages'][pi]
 raw=(root/'assets'/('map%03d_vm.bin'%mid)).read_bytes()
 for c in original['list']:
  if c['code']==250:
   q=c['parameters'][0];rid=ids[q['name'],q['volume'],q['pitch'],q['pan']];assert bytes([6])+struct.pack('<HBBB',rid,q['volume'],q['pitch'],q['pan']+100)in raw
   assert (root/'assets'/('se_exact_%04d.pcm'%rid)).stat().st_size>0
print('PASS: press phases, repeated cycles, disabled event, map exit, original death sound references and PCM files')
