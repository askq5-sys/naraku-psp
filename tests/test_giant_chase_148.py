"""Run the real chase scheduler against running/walking escape timings."""
from pathlib import Path
import runpy,subprocess,tempfile
r=Path(__file__).resolve().parents[1];s=(r/'main.c').read_text();n=runpy.run_path(str(r/'tests/test_s003_runtime.py'))
a=s.index('static int event_route_can_step(');b=s.index('static void tick_player_route(',a);body=s[a:b]
post=r'''static int chase(int tile_frames){MapState m={72,1};int px=44,py=5,tx=43,ty=5,elapsed=0;
for(int id=0;id<MAX_EVENT_ID;id++){free(g_routes[id].records);memset(&g_routes[id],0,sizeof(EventRoute));g_event_shift_x[id]=g_event_shift_y[id]=0;g_event_through[id]=1;g_event_move_speed[id]=5;}
const FactoryRoute*fr=NULL;for(unsigned int i=0;i<sizeof(factory_routes)/sizeof(factory_routes[0]);i++)if(factory_routes[i].map==72&&factory_routes[i].id==4)fr=&factory_routes[i];assert(fr);
EventRoute*q=&g_routes[4];q->records=malloc(fr->count*5);memcpy(q->records,fr->records,fr->count*5);q->count=fr->count;q->flags=fr->flags;q->base_x=50;q->base_y=5;
for(int f=0;f<1000;f++) {
float sx=g_event_shift_x[4];if(q->records&&q->remaining>0)sx=q->start_x+q->dx;
int enemy=50+(int)(sx+(sx<0?-.5f:.5f));
/* Match the port's conservative current/incoming player contact checks. */
if((py==5&&enemy==px)||(ty==5&&enemy==tx))return -(f+1);
tick_event_routes(&m);
if(++elapsed==tile_frames){px=tx;py=ty;elapsed=0;if(px==13&&py==6)return f+1;if(px>13){tx=px-1;ty=5;}else {tx=13;ty=6;}}
}
assert(0);return 0;}
int main(void){int running=chase(8),walking=chase(16);
#ifdef OLD_CHASE
assert(running<0);printf("Previous scheduler catches running Enri at frame %d\n",-running-1);
#else
assert(running==256&&walking<0);printf("Running reaches the exit at frame %d; walking still loses as intended\n",running);
/* A speed-change command gets its own update rather than starting a step. */
MapState m={72,1};free(g_routes[4].records);memset(&g_routes[4],0,sizeof(EventRoute));EventRoute*q=&g_routes[4];q->records=calloc(2,5);q->records[0]=29;q->records[1]=6;q->records[5]=2;q->count=2;float x=g_event_shift_x[4];tick_event_routes(&m);assert(g_event_move_speed[4]==6&&q->index==1&&g_event_shift_x[4]==x);tick_event_routes(&m);assert(g_event_shift_x[4]<x);
#endif
return 0;}'''
with tempfile.TemporaryDirectory()as td:
 for old in (False,True):
  code=body.replace('                if(m->id==72)break;','') if old else body
  p=Path(td)/'t.c';e=Path(td)/'t';p.write_text(n['pre']+n['globals_']+code+post)
  subprocess.run(['cc','-std=c99','-I',str(r),*(['-DOLD_CHASE']if old else[]),str(p),'-o',str(e)],check=True);subprocess.run([str(e)],check=True)
print('PASS: original giant-spider speeds and route preserved; speed changes consume their original frame; full running escape passes while old scheduler fails')
