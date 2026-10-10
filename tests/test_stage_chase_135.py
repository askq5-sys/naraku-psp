from pathlib import Path
import runpy, subprocess, tempfile
r=Path(__file__).resolve().parents[1];s=(r/'main.c').read_text()
def check(code):
    with tempfile.TemporaryDirectory()as td:
        p=Path(td)/'t.c';e=Path(td)/'t';p.write_text(code)
        subprocess.run(['cc','-std=c99','-I',str(r),str(p),'-o',str(e)],check=True);subprocess.run([str(e)],check=True)
n=runpy.run_path(str(r/'tests/test_s003_runtime.py'))
pre=n['pre'].replace('static int first,active,blocked_axis;', 'static int first,active,blocked_axis,test_id=3;').replace('{3,6,8,first}', '{test_id,6,8,first}')
a=s.index('static int event_route_can_step(');b=s.index('static void tick_player_route(',a)
post=r'''int main(void){
for(unsigned int k=0;k<sizeof(factory_routes)/sizeof(factory_routes[0]);k++){
const FactoryRoute*fr=&factory_routes[k];if(fr->map<48 || fr->records[0]!=10)continue;
MapState m={fr->map,1};test_id=fr->id;first=100;active=first+fr->page;
memset(g_factory_page,0,sizeof(g_factory_page));memset(g_routes,0,sizeof(g_routes));memset(g_event_shift_x,0,sizeof(g_event_shift_x));memset(g_event_shift_y,0,sizeof(g_event_shift_y));player_animation_reset(&g_event_animation[test_id]);g_s003_paused=0;
tick_s003_autonomous(&m,9.5f*24,3.f*24);tick_factory_autonomous(&m);assert(g_routes[test_id].records);
tick_event_routes(&m);assert(g_event_shift_y[test_id]<0&&g_event_direction[test_id]==3);
int animated=0;for(int i=0;i<50;i++){tick_event_routes(&m);if(g_event_animation[test_id].pattern!=1)animated=1;}assert(animated);
active=first+127;tick_factory_autonomous(&m);assert(!g_routes[test_id].records);
active=first+fr->page;g_s003_paused=1;tick_factory_autonomous(&m);assert(!g_routes[test_id].records);
}
return 0;}'''
check(pre+n['globals_']+s[a:b]+post)
n=runpy.run_path(str(r/'tests/test_killer_contact.py'))
pre=n['pre'].replace('test_supported=1;', 'test_supported=1,test_id=3;').replace('{3,6,8}', '{test_id,6,8}')
a=s.index('static int is_chase_enemy(');b=s.index('/* A supported active VM page',a)
post=r'''int main(void){int maps[]={49,50,51,52,53},ids[]={28,10,4,5,15};
for(int i=0;i<5;i++){MapState m={maps[i],1,(void*)1};test_id=ids[i];VmEventRecord e;VmPageRecord p;
g_routes[test_id]=(EventRoute){(void*)1,31,-1,0,0,0};g_event_shift_x[test_id]=-.03125f;g_event_shift_y[test_id]=0;
assert(is_chase_map(m.id)&&is_chase_enemy(m.id,test_id));assert(vm_event_blocks_at(&m,5,8));assert(!vm_event_blocks_at(&m,6,8));assert(vm_find_event_at(&m,5,8,2,&e,&p));assert(!vm_find_event_at(&m,6,8,2,&e,&p));
armed=0;assert(!vm_find_event_at(&m,5,8,2,&e,&p));armed=1;
}return 0;}'''
check(pre+s[a:b]+post)
print('PASS: actual C chase startup, gait, page cancellation, pause and one-cell collision for all five new chase rooms')
