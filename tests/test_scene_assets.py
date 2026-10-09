from pathlib import Path
import struct, subprocess, tempfile
root=Path(__file__).resolve().parents[1]
def records(map_id):
    raw=(root/'assets'/f'map{map_id:03d}_events.bin').read_bytes()
    count=struct.unpack_from('<H',raw,10)[0]
    return [struct.unpack_from('<6H2BH',raw,len(raw)-count*16+i*16) for i in range(count)]
r=records(12)
# Emma with tray must have a full walking sheet; Enri's special poses stay fixed.
assert any(x[8]==1 and x[7]&0x80 for x in r)
assert all(not(x[7]&0x80) for x in r if x[8]==2 and not(x[7]&0x40))
assert all(x[7]&4 for x in r)
axe=records(13)[0]
assert axe[8]==69 and axe[7]&4 and axe[7]&2
# Three original-resolution cleaver frames exist within the atlas.
assert axe[2]+axe[4]*3<=512 and axe[3]+axe[5]<=512
s=(root/'main.c').read_text();a=s.index('static void compute_camera(');b=s.index('static void draw_map_slot_local',a)
pre='''#include <assert.h>
#define TILE_PX 24
#define SCREEN_W 480
#define SCREEN_H 272
typedef struct {int id,w,h;} MapState;
static int g_camera_locked;
static float g_camera_lock_x,g_camera_lock_y,g_camera_scroll_x,g_camera_scroll_y;
static float clamp_float(float x,float lo,float hi){return x<lo?lo:x>hi?hi:x;}
'''
post='''int main(void){float x,y,ox,oy;MapState m={11,17,13};
compute_camera(&m,180,180,&x,&y,&ox,&oy);assert(ox+180-x==240);
m.id=13;m.w=21;m.h=15;
compute_camera(&m,100,180,&x,&y,&ox,&oy);assert(ox+228-x==240);
compute_camera(&m,400,180,&x,&y,&ox,&oy);assert(ox+228-x==240);
m.id=10;m.w=17;compute_camera(&m,204,180,&x,&y,&ox,&oy);assert(ox==36&&x==0);
return 0;}
'''
with tempfile.TemporaryDirectory() as tmp:
    p=Path(tmp)/'camera.c';exe=Path(tmp)/'camera';p.write_text(pre+s[a:b]+post)
    subprocess.run(['cc','-std=c99',str(p),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
print('PASS: tray walking frames, fixed story poses, original-resolution cleaver and room centring')
