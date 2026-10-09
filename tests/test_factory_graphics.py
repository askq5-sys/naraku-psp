from pathlib import Path
import json,struct,sys,subprocess,tempfile
from PIL import Image
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'tools'));import prepare_world_v060 as w
system=json.load(open(r.parent/'original/data/System.json'));key=bytes.fromhex(system['encryptionKey']);tilesets=json.load(open(r.parent/'original/data/Tilesets.json'));counts={'native_frames':0,'collision_pages':0,'pass_cells':0,'filtered_tiles':0}
for mid in range(32,36):
 m=json.load(open(r.parent/f'original/data/Map{mid:03}.json'));mw,mh=m['width'],m['height'];ts=tilesets[m['tilesetId']];bitmaps={}
 for n,name in enumerate(ts['tilesetNames']):
  if name:bitmaps[n]=w.load_encrypted_png(w.resolve_named_file(r.parent/'original/img/tilesets',name),key)
 mb=(r/'assets'/f'map{mid:03}.bin').read_bytes();slots={tid:i+1 for i,tid in enumerate(sorted(set(m['data'][:mw*mh*4])-{0}))}
 for i,tid in enumerate(m['data'][:mw*mh*4]):
  word=struct.unpack_from('<H',mb,20+i*2)[0];assert(word&0x3FFF)==slots.get(tid,0)
  filtered=tid in(135,143,151,161,162);assert bool(word&0x4000)==filtered;counts['filtered_tiles']+=filtered
 for y in range(mh):
  for x in range(mw):assert mb[20+mw*mh*8+y*mw+x]==w.build_pass_mask(m,ts['flags'],x,y);counts['pass_cells']+=1
 vb=(r/'assets'/f'map{mid:03}_vm.bin').read_bytes();_,ne,np,_,_,_=struct.unpack_from('<4sHHIII',vb);base=20+ne*10
 eb=(r/'assets'/f'map{mid:03}_events.bin').read_bytes();_,_,_,nt,ns,_=struct.unpack_from('<4s5H',eb);sb=14+mw*mh*5+nt*20
 atlases=[Image.frombytes('RGBA',(512,512),(r/'assets'/f'map{mid:03}_event_atlas.rgba8888').read_bytes())]
 if mid==32:atlases.append(Image.frombytes('RGBA',(512,512),(r/'assets/map032_event_atlas1.rgba8888').read_bytes()))
 for i in range(ne):
  eid,x,y,first,n,_=struct.unpack_from('<HHHHBB',vb,20+i*10);ev=m['events'][eid];assert(x,y)==(ev['x'],ev['y'])
  for j,p in enumerate(ev['pages']):
   pg=struct.unpack_from('<BBBBHHBBHII',vb,base+(first+j)*20)
   assert pg[2]==p['priorityType'] and bool(pg[3]&1)==p['through'];assert pg[0:1]==(w.vm_page_conditions(p)[0],);assert(pg[4],pg[5],pg[6])==w.vm_page_conditions(p)[1:];counts['collision_pages']+=1
   ref=pg[8]
   if not ref:continue
   rec=struct.unpack_from('<6H2BH',eb,sb+(ref-1)*16);sx,sy,sw,sh=rec[2:6];page=sx>>12;sx&=0xFFF;assert page<len(atlases)
   image=p['image'];name=image['characterName'];tile=image['tileId']
   if name not in('!プレス機','!死体詰箱','!死体詰箱2','ベルトコンベア')and not tile:continue
   if tile:frame=w.render_tile(tile,bitmaps)
   else:
    src=w.load_encrypted_png(w.resolve_named_file(r.parent/'original/img/characters',name),key);frame=w.extract_character_frame(src,name,image['characterIndex'],image['direction'],image['pattern'])
   if mid in (33,34) and name in ('!死体詰箱','!死体詰箱2'):
    frame=frame.resize((frame.width//2,frame.height//2),Image.Resampling.LANCZOS).resize(frame.size,Image.Resampling.NEAREST)
   assert rec[7]&4 and(sw,sh)==frame.size
   # The rotating conveyor strip's selected source direction is in its matching row.
   if rec[7]&64:sy+=(image['direction']//2-1)*sh
   expected=Image.new('RGBA',frame.size);expected.alpha_composite(frame)
   assert atlases[page].crop((sx,sy,sx+sw,sy+sh)).tobytes()==expected.tobytes();counts['native_frames']+=1
# Actual renderer must mask texture-page bits, bind the right atlas and preserve display sizes.
s=(r/'main.c').read_text();a=s.index('static void draw_event_sprite_record(');b=s.index('static int is_dedicated_story_key_event(',a)
pre='''#include <assert.h>
#include <stdint.h>
#include <string.h>
#define MAX_EVENT_ID 160
#define TILE_PX 24
#define EVENT_ATLAS_W 512
#define EVENT_ATLAS_H 512
#define GU_LINEAR 1
#define GU_NEAREST 0
#define GU_TFX_MODULATE 1
#define GU_TCC_RGBA 1
typedef struct{int x,y,sx,sy,sw,sh,flags,event_id;}EventSpriteRecord;
typedef struct{void *records;int remaining,dx,dy;}EventRoute;
static EventRoute g_routes[160];static float g_event_shift_x[160],g_event_shift_y[160],g_event_jump_height[160],g_actor_camera_x,g_actor_camera_y;
static int g_event_direction[160],g_event_opacity[160];static struct{int pattern;}g_event_animation[160];static unsigned int g_world_render_frames;
static void *g_event_texture_base=(void*)1,*g_event_texture_detail=(void*)2,*g_event_texture_bound;
static void *bound;static float srcx,dstw,dsth;static int filter;
static int is_chase_enemy(int m,int id){return (m==32&&id==23);}
static float render_floor_pixel(float x){return (int)x;}
static void bind_texture_8888(void*p,int w,int h){bound=p;}
static void sceGuTexFilter(int a,int b){filter=a;}
static void sceGuTexFunc(int a,int b){}
static void sceGuColor(unsigned int a){}
static void set_pixel_art_texture_state(void){}
static void draw_bound_rect(float x,float y,float w,float h,float dx,float dy,float dw,float dh){srcx=x;dstw=dw;dsth=dh;}
'''
post='''int main(void){for(int i=0;i<160;i++)g_event_opacity[i]=255;g_event_direction[2]=-1;
EventSpriteRecord press={5,0,4097,1,336,384,5,2};draw_event_sprite_record(&press,32,0,0,0,0);assert(bound==(void*)2&&srcx==1&&dstw==168&&dsth==192&&filter==GU_LINEAR);
EventSpriteRecord box={7,5,10,20,144,96,5,1};draw_event_sprite_record(&box,33,0,0,0,0);assert(bound==(void*)1&&srcx==10&&dstw==72&&dsth==48&&filter==GU_NEAREST);
EventSpriteRecord tile={2,17,4097,1,48,48,5,19};draw_event_sprite_record(&tile,32,0,0,0,0);assert(bound==(void*)2&&srcx==1&&dstw==24&&dsth==24);return 0;}'''
with tempfile.TemporaryDirectory()as tmp:
 p=Path(tmp)/'t.c';e=Path(tmp)/'t';p.write_text(pre+s[a:b]+post);subprocess.run(['cc','-std=c99',str(p),'-o',str(e)],check=True);subprocess.run([str(e)],check=True)
assert 'm->id>=32 && m->id<=45' in s and 'free(m->event_atlas_detail)'in s
(r/'audit_factory_graphics_129.json').write_text(json.dumps(counts,indent=2))
print('PASS:',counts,'native/prefiltered source pixels, all collider pages and tile passage masks; actual detail texture selection and unchanged display size')
