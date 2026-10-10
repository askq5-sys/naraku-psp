from pathlib import Path
import re,struct,sys,tempfile,subprocess
from PIL import Image
r=Path(__file__).resolve().parents[1];g=r.parent/'original'
sys.path.insert(0,str(r/'tools'));import prepare_world_v060 as w
header=(r/'runtime/factory_routes.h').read_text()
mp=w.read_json(g/'data/Map095.json');routes=0
for e in mp['events']:
 if not e:continue
 for i,p in enumerate(e['pages']):
  if p['moveType']!=3:continue
  raw=w.compile_vm_commands({'list':[{'code':205,'indent':0,'parameters':[e['id'],p['moveRoute']]},{'code':0,'indent':0,'parameters':[]}]},{})
  _,n,flags=struct.unpack_from('<hHB',raw,1)
  name=f'will_route_95_{e["id"]}_{i}'
  actual=bytes(map(int,re.search(name+r'\[\] = \{([^}]+)',header)[1].split(',')))
  assert actual==raw[6:6+n*5]
  assert f'{{95,{e["id"]},{i},{n},{flags},{name}}}' in header
  routes+=1
assert routes==5
s=(r/'main.c').read_text();start=s.index('static void tick_factory_autonomous(');end=s.index('static void tick_player_route(',start)
pre='''#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#define MAX_EVENT_ID 128
typedef struct {uint8_t*records;} EventRoute;
typedef struct {int id,vm_event_count;} MapState;
typedef struct {int event_id,first_page;} VmEventRecord;
typedef struct {int unused;} VmPageRecord;
static EventRoute g_routes[128];static int g_factory_page[128],g_s003_paused,changed,started[128];
static const int ids[5]={3,4,6,7,9};
static int vm_read_event(const MapState*m,int i,VmEventRecord*e){e->event_id=ids[i];e->first_page=100+i*3;return 1;}
static int vm_active_page_index(const MapState*m,const VmEventRecord*e,VmPageRecord*p,int*a){*a=e->first_page+(e->event_id<=6?2:1);if(changed)*a=e->first_page;return 1;}
static int start_event_route(const MapState*m,int id,const uint8_t*p,int n,int flags){g_routes[id].records=malloc(1);started[id]++;return 1;}
#include "runtime/factory_routes.h"
'''
post='''int main(void){MapState m={95,5};tick_factory_autonomous(&m);for(int i=0;i<5;i++)assert(started[ids[i]]==1);tick_factory_autonomous(&m);for(int i=0;i<5;i++)assert(started[ids[i]]==1);changed=1;tick_factory_autonomous(&m);for(int i=0;i<5;i++)assert(!g_routes[ids[i]].records);changed=0;g_s003_paused=1;tick_factory_autonomous(&m);for(int i=0;i<5;i++)assert(!g_routes[ids[i]].records);g_s003_paused=0;tick_factory_autonomous(&m);for(int i=0;i<5;i++){assert(started[ids[i]]==2);free(g_routes[ids[i]].records);}return 0;}'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'t.c';exe=Path(td)/'t';p.write_text(pre+s[start:end]+post)
 subprocess.run(['cc','-std=c99','-I',str(r),str(p),'-o',str(exe)],check=True);subprocess.run([str(exe)],check=True)
# All moving pursuers have native walking frames for every direction.
b=(r/'assets/map095_events.bin').read_bytes();mw,mh,nt,ns=struct.unpack_from('<4H',b,4);base=14+mw*mh*5+nt*20
for eid in (3,4,6,7,9):
 assert any(sp[-1]==eid and sp[7]&0xC4==0xC4 for sp in [struct.unpack_from('<6H2BH',b,base+i*16)for i in range(ns)])
key=bytes.fromhex(w.read_json(g/'data/System.json')['encryptionKey'])
source=w.load_encrypted_png(w.resolve_named_file(g/'img/system','Balloon'),key)
atlas=Image.frombytes('RGBA',(512,512),(r/'assets/balloon_atlas.rgba8888').read_bytes())
for row in range(10):
 for frame in range(8):
  expected=Image.new('RGBA',(48,48));expected.alpha_composite(source.crop((frame*48,row*48,frame*48+48,row*48+48)))
  assert atlas.crop((frame*50+1,row*50+1,frame*50+49,row*50+49)).tobytes()==expected.tobytes()
print('PASS: all five original chase routes, actual autonomous scheduler activation/cancellation/pause, native walking sheets and 80 original balloon frames')
