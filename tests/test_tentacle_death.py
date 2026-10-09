from pathlib import Path
import json,struct,sys,subprocess,tempfile
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'tools'));import prepare_world_v060 as w
texts=json.load(open(r.parent/'original/data/I18NTexts.json'));w.PICTURE_IDS=json.load(open(r.parent/'port/assets/picture_v050_manifest.json'));audio=json.load(open(r/'assets/audio_exact_v079.json'));w.EXACT_SE_IDS={w.audio_key(x):int(x['id'])for x in audio if x['kind']=='se'};w.EXACT_BGM_IDS={w.audio_key(x):int(x['id'])for x in audio if x['kind']=='bgm'}
for mid in (15,16):
 m=json.load(open(r.parent/f'original/data/Map{mid:03d}.json'));raw=(r/'assets'/f'map{mid:03d}_vm.bin').read_bytes();_,ne,np,blob,size,flags=struct.unpack_from('<4sHHIII',raw);assert flags&1;base=20+ne*10
 evraw=(r/'assets'/f'map{mid:03d}_events.bin').read_bytes();_,mw,mh,nt,ns,_=struct.unpack_from('<4s5H',evraw);sprbase=14+mw*mh*5+nt*20
 records=[struct.unpack_from('<6H2BH',evraw,sprbase+i*16)for i in range(ns)]
 for i in range(ne):
  eid,x,y,first,n,_=struct.unpack_from('<HHHHBB',raw,20+i*10);event=m['events'][eid];assert n==len(event['pages'])
  for j,page in enumerate(event['pages']):
   pg=struct.unpack_from('<BBBBHHBBHII',raw,base+(first+j)*20);ref,off,length=pg[8:];assert pg[7]==1
   assert raw[blob+off:blob+off+length]==w.compile_vm_commands(page,texts)
   image=page['image'];visible=bool(image['characterName']or image['tileId']);assert bool(ref)==visible
   if ref:
    rec=records[ref-1];assert rec[-1]==eid
    sx,sy,sw,sh=rec[2:6];nframes=3 if rec[7]&2 else 1
    assert sx+sw*nframes<=512 and sy+sh<=512
    if mid==15 and eid in (7,8):assert (sw,sh)==(48,144)and rec[7]&4
    if mid==16 and eid==36:assert(sw,sh)==(80,80)and rec[7]&4
# Every death-scene sound keeps the exact volume/pitch PCM and exists in the patch.
for mid,eid in ((15,10),(15,11),(16,35)):
 page=json.load(open(r.parent/f'original/data/Map{mid:03d}.json'))['events'][eid]['pages'][0]
 for cmd in page['list']:
  if cmd['code']==250:
   audio=cmd['parameters'][0];aid=w.EXACT_SE_IDS[w.audio_key(audio)];assert(r/'assets'/f'se_exact_{aid}.pcm').stat().st_size>0
s=(r/'main.c').read_text();a=s.index('static void draw_tentacle_room_sprites(');b=s.index('static void draw_event_sprites(',a)
pre='''#include <assert.h>
#define MAX_EVENT_ID 160
#define TILE_PX 24
typedef struct{int vm_event_count,id;}MapState;
typedef struct{int event_id,y;}VmEventRecord;
typedef struct{int priority,sprite_ref,flags;}VmPageRecord;
typedef struct{int event_id;}EventSpriteRecord;
static float g_event_shift_y[160],g_event_jump_height[160];static int g_event_active_page[160],g_event_direction[160],g_event_move_speed[160],g_event_direction_fix[160],g_event_through[160],g_event_opacity[160],g_event_animation[160];
static const int ids[]={1,2,3,36},ysrc[]={13,7,11,0};static int order[160],count;
static int vm_read_event(const MapState*m,int i,VmEventRecord*e){e->event_id=ids[i];e->y=ysrc[i];return 1;}
static int vm_active_page_index(const MapState*m,const VmEventRecord*e,VmPageRecord*p,int*a){*a=1;p->priority=1;p->sprite_ref=e->event_id;p->flags=24;return 1;}
static int read_sprite_record(const MapState*m,int i,EventSpriteRecord*p){p->event_id=i+1;return 1;}
static void player_animation_reset(int*a){}
static void draw_event_sprite_record(const EventSpriteRecord*s,int mid,float x,float y,float ox,float oy){order[count++]=s->event_id;}
'''
post='''int main(void){MapState m={4,16};
g_event_shift_y[36]=6;draw_tentacle_room_sprites(&m,1,0,0,0,0,0,0);assert(count==4&&order[0]==36&&order[3]==1);
count=0;g_event_shift_y[36]=12;draw_tentacle_room_sprites(&m,1,0,0,0,0,0,0);assert(order[0]==2&&order[1]==3&&order[2]==36&&order[3]==1);
count=0;draw_tentacle_room_sprites(&m,1,-1,240,0,0,0,0);assert(count==1&&order[0]==2);
count=0;draw_tentacle_room_sprites(&m,1,1,240,0,0,0,0);assert(count==3&&order[2]==1);
return 0;}'''
with tempfile.TemporaryDirectory()as tmp:
 p=Path(tmp)/'t.c';e=Path(tmp)/'t';p.write_text(pre+s[a:b]+post);subprocess.run(['cc','-std=c99','-Wall',str(p),'-o',str(e)],check=True);subprocess.run([str(e)],check=True)
print('PASS: every original page/choice/switch/wait/transfer command preserved, all poses present, atlas bounds, exact sounds and actual depth sorting behind foreground tentacles')
