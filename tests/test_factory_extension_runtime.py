from pathlib import Path
import subprocess,tempfile,runpy
r=Path(__file__).resolve().parents[1];s=(r/'main.c').read_text()
def compile_run(code):
 with tempfile.TemporaryDirectory()as tmp:
  p=Path(tmp)/'t.c';e=Path(tmp)/'t';p.write_text(code);subprocess.run(['cc','-std=c99','-I',str(r),str(p),'-o',str(e)],check=True);subprocess.run([str(e)],check=True)
a=s.index('static int number_input_change_digit(');b=s.index('static void fade_game_world(',a)
pre='''#include <stdint.h>
#include <assert.h>
#define PSP_CTRL_UP 1
#define PSP_CTRL_DOWN 2
#define PSP_CTRL_LEFT 4
#define PSP_CTRL_RIGHT 8
#define SE_UI_CURSOR_PATH 1
#define SE_UI_OK_PATH 2
#define SE_UI_BUZZER_PATH 3
typedef struct{int id;}MapState;
typedef struct{uint32_t Buttons;}SceCtrlData;
static int g_number_active,g_number_digits,g_number_cursor,g_number_value;
static unsigned int buttons[]={0,1,0,4,0,2,0,8,0,16},poll,frames;
static void sceCtrlPeekBufferPositive(SceCtrlData*p,int n){assert(poll<sizeof(buttons)/sizeof(buttons[0]));p->Buttons=buttons[poll++];}
static void play_se_async(int s){}
static uint32_t ui_ok_mask(void){return 16;}
static uint32_t ui_cancel_mask(void){return 32;}
static void vm_render_frame(const MapState*m,void*a,int x,int y,int d,int b,int f){assert(g_number_active);frames++;}
'''
post='''int main(void){MapState m={45};assert(vm_wait_number_input(&m,0,0,0,0,0,4)==1009);assert(!g_number_active&&g_number_cursor==0&&frames==9);
for(int digits=1;digits<=8;digits++)for(int cursor=0;cursor<digits;cursor++){
 int place=1;for(int i=cursor+1;i<digits;i++)place*=10;
 assert(number_input_change_digit(0,digits,cursor,-1)==9*place);
 assert(number_input_change_digit(9*place,digits,cursor,1)==0);
 assert(number_input_change_digit(3*place,digits,cursor,1)==4*place);
}return 0;}'''
compile_run(pre+s[s.index("static unsigned int g_ambush_reveal_start;"):s.index("static void draw_event_sprite_record(")]+s[a:b]+post)
# Run the new fade opcode's actual body and retain black through subsequent waits.
a=s.index('        } else if (op == VM_OP_FADE_SCREEN) {');b=s.index('        } else if (op == VM_OP_SWITCH) {',a)
body=s[a:b].split('{',1)[1]
pre='''#include <stdint.h>
#include <assert.h>
typedef struct{int id;}MapState;
static int g_script_fade_alpha,frames,last;
static void vm_render_frame(MapState*m,void*a,int x,int y,int d,int b,int r){assert(g_script_fade_alpha>=0&&g_script_fade_alpha<=255);last=g_script_fade_alpha;frames++;}
static void command(MapState*m,int out){uint8_t data=out;const uint8_t*p=&data,*end=p+1;int x=0,y=0,d=0,*tile_x=&x,*tile_y=&y,*direction_row=&d;void*char_atlas=0;
while(1){
'''
post='''break;}}
int main(void){MapState m={36};command(&m,1);assert(frames==24&&last==255&&g_script_fade_alpha==255);m.id=37;vm_render_frame(&m,0,0,0,0,0,0);assert(last==255);command(&m,0);assert(frames==49&&last==0&&g_script_fade_alpha==0);return 0;}'''
compile_run(pre+body+post)
# Actual route scheduler animates both sensor directions and cancels an inactive page.
n=runpy.run_path(str(r/'tests/test_s003_runtime.py'));pre=n['pre'];glob=n['globals_']
pre=pre.replace('static int first,active,blocked_axis;','static int first,active,blocked_axis,test_id=5;').replace('{3,6,8,first}','{test_id,6,8,first}')
a=s.index('static int event_route_can_step(');b=s.index('static void tick_player_route(',a)
post='''int main(void){MapState m={43,1};first=7;active=first;test_id=5;
tick_factory_autonomous(&m);assert(g_routes[5].records);tick_event_routes(&m);assert(g_event_direction[5]==0);tick_event_routes(&m);assert(g_event_direction[5]==1);tick_event_routes(&m);assert(g_event_direction[5]==2);tick_event_routes(&m);assert(g_event_direction[5]==3);
active=first+1;tick_factory_autonomous(&m);assert(!g_routes[5].records);
test_id=8;tick_factory_autonomous(&m);assert(g_routes[8].records);tick_event_routes(&m);assert(g_event_direction[8]==0);tick_event_routes(&m);assert(g_event_direction[8]==1);
g_s003_paused=1;active=first;tick_factory_autonomous(&m);assert(g_routes[8].records);g_s003_paused=0;tick_factory_autonomous(&m);assert(!g_routes[8].records);
m.id=39;for(int id=2;id<=4;++id)player_animation_reset(&g_event_animation[id]);for(int i=0;i<40;++i)tick_event_routes(&m);for(int id=2;id<=4;++id)assert(g_event_animation[id].pattern!=1);return 0;}'''
compile_run(pre+glob+s[a:b]+post)
# Actual renderer decodes packed four-direction sensor and twelve-frame actors.
n=runpy.run_path(str(r/'tests/test_factory_graphics.py'));pre=n['pre'].replace('static float srcx,dstw,dsth;', 'static float srcx,srcy,dstw,dsth;').replace('srcx=x;dstw=dw;', 'srcx=x;srcy=y;dstw=dw;')
a=s.index('static void draw_event_sprite_record(');b=s.index('static int is_dedicated_story_key_event(',a)
post='''int main(void){for(int i=0;i<160;i++)g_event_opacity[i]=255;
EventSpriteRecord sensor={7,5,1,1,48,192,69,5};for(int row=0;row<4;row++){g_event_direction[5]=row;draw_event_sprite_record(&sensor,43,0,0,0,0);assert(srcx==1+(row&1)*48&&srcy==1+(row>>1)*192&&dstw==24&&dsth==96);}
EventSpriteRecord lever={12,4,4097,1,108,324,5,1};draw_event_sprite_record(&lever,40,0,0,0,0);assert(bound==(void*)2&&dstw==72&&dsth==216);
EventSpriteRecord actor={8,10,1,1,48,78,196,4};for(int row=0;row<4;row++)for(int pat=0;pat<3;pat++){g_event_direction[4]=row;g_event_animation[4].pattern=pat;draw_event_sprite_record(&actor,39,0,0,0,0);assert(srcx==1+((row&1)*3+pat)*48&&srcy==1+(row>>1)*78&&dstw==24&&dsth==39);}
EventSpriteRecord giant={8,10,1,1,240,192,132,2};for(int pat=0;pat<3;pat++){g_event_animation[2].pattern=pat;draw_event_sprite_record(&giant,72,0,0,0,0);assert(srcx==1+(pat&1)*240&&srcy==1+(pat>>1)*192&&dstw==120&&dsth==96);}
EventSpriteRecord key={5,5,1,1,48,48,30,12};int poses=0;for(int f=0;f<72;f++){g_world_render_frames=f;draw_event_sprite_record(&key,43,0,0,0,0);if(srcx!=49)poses++;}assert(poses);return 0;}'''
compile_run(pre+s[s.index("static unsigned int g_ambush_reveal_start;"):s.index("static void draw_event_sprite_record(")]+s[a:b]+post)
print('PASS: actual C number-input navigation/digit wrap, persistent 24-frame fade, sensor startup/directions/page cancel, classroom stepping, packed sensor/actor atlas coordinates, crank display size, key animation')
