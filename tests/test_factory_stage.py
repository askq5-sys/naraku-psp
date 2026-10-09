from pathlib import Path
import json,struct,sys,runpy,subprocess,tempfile
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'tools'));import prepare_world_v060 as w
w.PICTURE_IDS=json.load(open(r.parent/'port/assets/picture_v050_manifest.json'));audio=json.load(open(r/'assets/audio_exact_v079.json'));w.EXACT_SE_IDS={w.audio_key(x):x['id']for x in audio if x['kind']=='se'};w.EXACT_BGM_IDS={w.audio_key(x):x['id']for x in audio if x['kind']=='bgm'};texts=json.load(open(r.parent/'original/data/I18NTexts.json'))
report=[]
for mid in range(32,36):
 m=json.load(open(r.parent/f'original/data/Map{mid:03}.json'));b=(r/'assets'/f'map{mid:03}_vm.bin').read_bytes();_,ne,np,blob,_,_=struct.unpack_from('<4sHHIII',b);base=20+ne*10
 eb=(r/'assets'/f'map{mid:03}_events.bin').read_bytes();_,mw,mh,nt,ns,_=struct.unpack_from('<4s5H',eb);sb=14+mw*mh*5+nt*20;records=[struct.unpack_from('<6H2BH',eb,sb+i*16)for i in range(ns)]
 for i in range(ne):
  eid,x,y,first,n,_=struct.unpack_from('<HHHHBB',b,20+i*10)
  for j,page in enumerate(m['events'][eid]['pages']):
   pg=struct.unpack_from('<BBBBHHBBHII',b,base+(first+j)*20);ref,off,length=pg[8:]
   assert pg[7]==int(not(mid==32 and eid==20 and j==1))
   if pg[7]:assert b[blob+off:blob+off+length]==w.compile_vm_commands(page,texts)
   visible=bool(page['image']['characterName']or page['image']['tileId']);assert bool(ref)==visible
   if ref:
    rec=records[ref-1];assert rec[-1]==eid;sx,sy,sw,sh=rec[2:6];page_index=sx>>12;sx&=0xFFF;assert page_index in (0,1)and (page_index==0 or mid==32);flags=rec[7]
    if page['image']['characterName']=='S-003':assert(flags&0xC4)==0xC4 and(sw,sh)==(54,108);assert sx+6*sw<=512 and sy+2*sh<=512
    else:assert sx+sw*(3 if flags&2 else 1)<=512 and sy+sh*(4 if flags&64 else 1)<=512
   for c in page['list']:
    if c['code']==231 and c['parameters'][1]!='A1':assert(r/'assets'/f"pic_{w.PICTURE_IDS[c['parameters'][1]]:03}.p44").is_file()
    if c['code']in(241,250)and c['parameters'][0]['name']:
     kind='bgm'if c['code']==241 else'se';ids=w.EXACT_BGM_IDS if kind=='bgm'else w.EXACT_SE_IDS;assert(r/'assets'/f'{kind}_exact_{ids[w.audio_key(c["parameters"][0])]}.pcm').stat().st_size>0
 report.append({'map':mid,'pages':np,'compiled':np-(mid==32),'dedicated_parallel':1 if mid==32 else 0})
# Actual route data must preserve every original autonomous command/parameter.
h=(r/'runtime/factory_routes.h').read_text()
import re
for mid in range(32,35):
 m=json.load(open(r.parent/f'original/data/Map{mid:03}.json'))
 for e in m['events']:
  if not e:continue
  for j,p in enumerate(e['pages']):
   if p['moveType']!=3:continue
   name=f'factory_route_{mid}_{e["id"]}_{j}';data=bytes(map(int,re.search(name+r'\[\] = \{([^}]+)',h)[1].split(',')))
   expected=b''.join(struct.pack('<Bhh',rc['code'],*(list(rc.get('parameters')or[])+[0,0])[:2])for rc in p['moveRoute']['list']if rc['code'])
   assert data==expected
# Exercise new scheduler and machine parallel pages using actual runtime C.
s=(r/'main.c').read_text();n=runpy.run_path(str(r/'tests/test_s003_runtime.py'));pre=n['pre'];glob=n['globals_']
pre=pre.replace('static int first,active,blocked_axis;','static int first,active,blocked_axis,test_id=3;').replace('{3,6,8,first}','{test_id,6,8,first}')
pre=pre.replace('static void play_vm_se_params(int a,int b,int c,int d){}','static int sounds;static void play_vm_se_params(int a,int b,int c,int d){++sounds;}\nstatic void vm_begin_screen_flash(int a,int b,int c,int d,int f){}\nstatic unsigned char g_switches[1024];')
a=s.index('static int event_route_can_step(');b=s.index('static void tick_player_route(',a);engine=s[a:b]
a=s.index('static void tick_factory_parallel(');b=s.index('static void render_world(',a);parallel=s[a:b]
post='''int main(void){MapState m={32,1};test_id=23;first=7;active=first+1;g_s003_paused=0;
tick_factory_autonomous(&m);assert(g_routes[23].records);tick_event_routes(&m);assert(g_event_shift_y[23]<0);
active=first;tick_factory_autonomous(&m);assert(!g_routes[23].records);
memset(g_event_animation,0,sizeof(g_event_animation));player_animation_reset(&g_event_animation[3]);m.id=30;
int legs=0;for(int i=0;i<100;i++){tick_event_routes(&m);if(g_event_animation[3].pattern!=1)legs=1;}assert(legs);
m.id=32;test_id=19;active=first+1;g_switches[256]=1;tick_factory_parallel(&m);assert(g_routes[19].records);
for(int i=0;i<500;i++){tick_event_routes(&m);tick_factory_parallel(&m);}
assert(!g_switches[256]&&!g_switches[258]&&!g_routes[19].records);assert(g_event_shift_x[19]==-10 && g_event_shift_y[19]==2);
g_switches[237]=g_switches[257]=1;sounds=0;
for(int i=0;i<299;i++)tick_factory_parallel(&m);assert(!sounds&&!g_switches[233]);
tick_factory_parallel(&m);assert(sounds==1&&g_switches[233]&&g_switches[235]&&!g_switches[234]);
for(int i=0;i<10;i++)tick_factory_parallel(&m);assert(g_switches[234]&&g_switches[236]&&!g_switches[233]);
for(int i=310;i<430;i++)tick_factory_parallel(&m);assert(!g_switches[237]&&!g_switches[257]&&!g_switches[233]&&!g_switches[234]&&sounds==2);assert(g_event_shift_x[19]==0&&g_event_shift_y[19]==0);
return 0;}'''
with tempfile.TemporaryDirectory()as tmp:
 p=Path(tmp)/'t.c';e=Path(tmp)/'t';p.write_text(pre+glob+engine+parallel+post);subprocess.run(['cc','-std=c99','-I',str(r),str(p),'-o',str(e)],check=True);subprocess.run([str(e)],check=True)
# Room centering: source passage is x7, i.e. foot centre x7.5, not map x8.5.
a=s.index('static void compute_camera(');b=s.index('static void draw_map_slot_local(',a)
pre='''#include <assert.h>
#define SCREEN_W 480
#define SCREEN_H 272
#define TILE_PX 24
typedef struct{int id,w,h;}MapState;
static int g_camera_locked;static float g_camera_lock_x,g_camera_lock_y,g_camera_scroll_x,g_camera_scroll_y;
static float clamp_float(float x,float a,float b){return x<a?a:(x>b?b:x);}
'''
post='''int main(void){float cx,cy,ox,oy;for(int id=21;id<=27;id++){if(id!=21&&id!=23&&id!=27)continue;MapState m={id,17,15};compute_camera(&m,180,100,&cx,&cy,&ox,&oy);assert(ox+7.5f*24-cx==240);}return 0;}'''
with tempfile.TemporaryDirectory()as tmp:
 p=Path(tmp)/'t.c';e=Path(tmp)/'t';p.write_text(pre+s[a:b]+post);subprocess.run(['cc','-std=c99',str(p),'-o',str(e)],check=True);subprocess.run([str(e)],check=True)
(r/'audit_factory_127.json').write_text(json.dumps(report,indent=2))
print('PASS: 326 factory pages accounted for, original commands/autonomous routes, picture/audio references, atlas bounds; actual chase/page cancel, Emma step animation, corpse routes, 430-frame nonblocking machine cycle, room centering')
