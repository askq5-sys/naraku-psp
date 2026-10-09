from pathlib import Path
import json,struct,sys,subprocess,tempfile,runpy
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'tools'));import prepare_world_v060 as w
T=json.load(open(r.parent/'original/data/I18NTexts.json'));w.PICTURE_IDS=json.load(open(r.parent/'port/assets/picture_v050_manifest.json'));audio=json.load(open(r/'assets/audio_exact_v079.json'));w.EXACT_SE_IDS={w.audio_key(x):int(x['id'])for x in audio if x['kind']=='se'};w.EXACT_BGM_IDS={w.audio_key(x):int(x['id'])for x in audio if x['kind']=='bgm'}
report=[]
for mid in range(14,32):
 path=r/'assets'/f'map{mid:03d}_vm.bin'
 if not path.exists():path=r.parent/'port/assets'/path.name
 b=path.read_bytes();_,ne,np,blob,size,flags=struct.unpack_from('<4sHHIII',b);base=20+ne*10
 unsupported=[]
 for i in range(ne):
  eid,x,y,first,n,_=struct.unpack_from('<HHHHBB',b,20+i*10)
  for j in range(n):
   if b[base+(first+j)*20+9]==0:unsupported.append((eid,j))
 assert unsupported==([(12,0)]if mid==24 else [])
 source=json.load(open(r.parent/f'original/data/Map{mid:03d}.json'))
 for i in range(ne):
  eid,x,y,first,n,_=struct.unpack_from('<HHHHBB',b,20+i*10)
  for j,page in enumerate(source['events'][eid]['pages']):
   im=page['image'];ref=struct.unpack_from('<H',b,base+(first+j)*20+10)[0]
   if im['characterName']or im['tileId']:assert ref>0

 report.append({'map':mid,'pages':np,'compiled':np-len(unsupported),'special_runtime': 'press cycle'if mid==24 else None})
 if mid<28:continue
 m=json.load(open(r.parent/f'original/data/Map{mid:03d}.json'));assert flags&1
 for i in range(ne):
  eid,x,y,first,n,_=struct.unpack_from('<HHHHBB',b,20+i*10);ev=m['events'][eid];assert(x,y,n)==(ev['x'],ev['y'],len(ev['pages']))
  for j,p in enumerate(ev['pages']):
   pg=struct.unpack_from('<BBBBHHBBHII',b,base+(first+j)*20);ref,off,length=pg[8:];assert pg[7]
   assert b[blob+off:blob+off+length]==w.compile_vm_commands(p,T)
   for c in p['list']:
    if c['code']==231 and c['parameters'][1]!='A1':assert (r/'assets'/f"pic_{w.PICTURE_IDS[c['parameters'][1]]:03d}.p44").is_file()
    if c['code']in(241,250):
     a=c['parameters'][0]
     if a['name']:
      kind='bgm'if c['code']==241 else'se';aid=(w.EXACT_BGM_IDS if kind=='bgm'else w.EXACT_SE_IDS)[w.audio_key(a)];assert(r/'assets'/f'{kind}_exact_{aid}.pcm').stat().st_size
# Both corridor and flashback have original one-shot switch gates.
m=json.load(open(r.parent/'original/data/Map029.json'))
assert all(e['pages'][1]['conditions']['switch1Id']==246 for e in m['events'][1:6])
m=json.load(open(r.parent/'original/data/Map030.json'));assert m['events'][10]['pages'][1]['conditions']['switch1Id']==247
b=(r/'assets/map030_events.bin').read_bytes();_,mw,mh,nt,ns,_=struct.unpack_from('<4s5H',b);off=14+mw*mh*5+nt*20
for i in range(ns):
 rec=struct.unpack_from('<6H2BH',b,off+i*16);sx,sy,sw,sh=rec[2:6];flags=rec[7]
 assert flags&4
 if rec[-1]in(3,4):assert flags&128 and flags&64 and sx+sw*3<=512 and sy+sh*4<=512
 else:assert sx+sw<=512 and sy+sh<=512
s=(r/'main.c').read_text();n=runpy.run_path(str(r/'tests/test_s003_runtime.py'));pre=n['pre'];glob=n['globals_'];a=s.index('static int event_route_can_step(');b=s.index('static void tick_player_route(',a)
post='''int main(void){MapState m={30,1};uint8_t jump[]={14,0,0,0,0,15,10,0,0,0,14,0,0,0,0};
g_event_move_speed[1]=3;assert(start_event_route(&m,1,jump,3,0));
tick_event_routes(&m);assert(g_routes[1].jump_peak==7 && g_routes[1].remaining==13 && g_event_jump_height[1]==3.25f);
for(int i=0;i<6;i++)tick_event_routes(&m);assert(g_event_jump_height[1]==12.25f);
for(int i=0;i<7;i++)tick_event_routes(&m);assert(g_event_jump_height[1]==0 && g_event_shift_x[1]==0 && g_event_shift_y[1]==0);
for(int i=0;i<10;i++)tick_event_routes(&m);assert(g_event_jump_height[1]==0);tick_event_routes(&m);assert(g_event_jump_height[1]==3.25f);
for(int i=0;i<15;i++)tick_event_routes(&m);assert(!g_routes[1].records && g_event_jump_height[1]==0);
return 0;}'''
with tempfile.TemporaryDirectory()as tmp:
 p=Path(tmp)/'t.c';e=Path(tmp)/'t';p.write_text(pre+glob+s[a:b]+post);subprocess.run(['cc','-std=c99','-I',str(r),str(p),'-o',str(e)],check=True);subprocess.run([str(e)],check=True)
a=s.index('static void vm_begin_map_scroll(');b=s.index('static void compute_camera(',a)
pre='''#include <assert.h>
#define TILE_PX 24
static float g_camera_scroll_x,g_camera_scroll_y,g_map_scroll_start_x,g_map_scroll_start_y,g_map_scroll_target_x,g_map_scroll_target_y;
static int g_map_scroll_remaining,g_map_scroll_total;
'''
post='''int main(void){vm_begin_map_scroll(6,6,2);assert(g_camera_scroll_x==0 && g_map_scroll_remaining==384);tick_map_scroll();assert(g_camera_scroll_x==.375f);for(int i=1;i<384;i++)tick_map_scroll();assert(g_camera_scroll_x==144 && g_map_scroll_remaining==0);vm_begin_map_scroll(4,7,3);assert(g_camera_scroll_x==144);tick_map_scroll();assert(g_camera_scroll_x<144 && g_camera_scroll_x>143);for(int i=1;i<224;i++)tick_map_scroll();assert(g_camera_scroll_x==-24);return 0;}'''
with tempfile.TemporaryDirectory()as tmp:
 p=Path(tmp)/'t.c';e=Path(tmp)/'t';p.write_text(pre+s[a:b]+post);subprocess.run(['cc','-std=c99',str(p),'-o',str(e)],check=True);subprocess.run([str(e)],check=True)
(r/'audit_stage_126.json').write_text(json.dumps(report,indent=2))
print('PASS: current-stage page audit; complete next-stage command streams, portraits/audio, one-shot gates, directional frames; actual NPC jump/wait/repeat and asynchronous scroll cadence')
