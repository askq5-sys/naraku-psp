from pathlib import Path
import subprocess,tempfile,json,struct
root=Path(__file__).resolve().parents[1];s=(root/'main.c').read_text();a=s.index('static void tick_laser_room(');b=s.index('static void tick_pressing_room(',a)
pre='''#include <assert.h>
typedef struct {int id;} MapState;
static int g_laser_room_frame,g_laser_stop_count,g_laser_route_index,se;
static unsigned char g_switches[1601];static int g_event_direction[160];
static struct {void*records;}g_routes[160];
static void play_vm_se_params(int id,int v,int p,int pan){assert(id==1031&&v==50&&p==80&&pan==0);se++;}
'''
post='''int main(void){MapState m={26};for(int i=1;i<=499;i++){tick_laser_room(&m);assert(!g_switches[137]&&se==0);if(i==2)assert(g_event_direction[4]==1);if(i==3)assert(g_event_direction[4]==2);if(i==4)assert(g_event_direction[4]==3);}tick_laser_room(&m);assert(se==1&&g_switches[134]&&g_switches[135]&&g_switches[136]&&g_switches[137]);for(int i=0;i<500;i++)tick_laser_room(&m);assert(se==1);g_switches[137]=0;for(int i=0;i<99;i++)tick_laser_room(&m);m.id=14;tick_laser_room(&m);assert(g_laser_room_frame==0);return 0;}
'''
with tempfile.TemporaryDirectory()as tmp:
 p=Path(tmp)/'t.c';e=Path(tmp)/'t';p.write_text(pre+s[a:b]+post);subprocess.run(['cc',str(p),'-o',str(e)],check=True);subprocess.run([str(e)],check=True)
raw=(root/'assets/map012_vm.bin').read_bytes();assert b'thesematerials'not in raw and b'towait'not in raw and b'Mrs.Peliah'not in raw;assert b'these materials'in raw and b'to wait'in raw
rows=json.load(open(root/'assets/audio_exact_v079.json'));rid=next(x['id']for x in rows if x['name']=='Explosion4'and x['pitch']==120 and x['volume']==100);assert bytes([6])+struct.pack('<HBBB',rid,100,120,100)in(root/'assets/map026_vm.bin').read_bytes();assert(root/'assets'/('se_exact_%04d.pcm'%rid)).stat().st_size>0
# The special key pass is part of world drawing before tone, fade and pictures.
render=s[s.index('static void render_world('):s.index('static void vm_begin_screen_flash(',s.index('static void render_world('))]
assert render.index('draw_story_key_foreground')<render.index('if (g_world_tone_gray')
assert render.count('draw_story_key_foreground')==2
print('PASS: four sensor directions, 500-frame disable, one beep, map exit reset, Explosion4, corrected flashback text and key render order')
