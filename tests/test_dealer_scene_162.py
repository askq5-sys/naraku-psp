from pathlib import Path
import ast,json,sys,struct,subprocess
r=Path(__file__).resolve().parents[1];s=(r/'main.c').read_text();tree=ast.parse((r/'tests/test_s003_runtime.py').read_text());pre=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='pre'for t in n.targets));glob=s[s.index('static float g_event_shift_x'):s.index('static EventRoute g_player_route;')];body=s[s.index('static int event_route_can_step('):s.index('static void tick_player_route(')]
m=json.load(open(r.parent/'original/data/Map094.json'));coords=', '.join('{'+f'{e["x"]},{e["y"]}'+ '}' if e else '{0,0}' for e in m['events']);b=(r/'assets/map094.bin').read_bytes();mask=b[20+m['width']*m['height']*8:20+m['width']*m['height']*9];priorities=[e['pages'][-1]['priorityType'] if e else 0 for e in m['events']];flags=[(int(e['pages'][-1]['through'])|(e['pages'][-1]['moveSpeed']<<2)|((e['pages'][-1]['image']['direction']//2-1)<<5)) if e else 0 for e in m['events']]
pre=pre.replace('static int first,active,blocked_axis;',f'static int coords[][2]={{{coords}}};static int priorities[]={{{",".join(map(str,priorities))}}};static int flags[]={{{",".join(map(str,flags))}}};static uint8_t masks[]={{{",".join(map(str,mask))}}};\nstatic int blocks(int,int,int);')
pre=pre.replace('*e=(VmEventRecord){3,6,8,first};','*e=(VmEventRecord){i+1,coords[i+1][0],coords[i+1][1],0};')
pre=pre.replace('p->flags=12;*i=active;','p->flags=flags[e->event_id];*i=0;')
pre=pre.replace('return blocked_axis && x==6 && y==8 ? 7 : 15;','return x<0||y<0||x>=20||y>=30?0:masks[y*20+x];')
pre=pre.replace('return 0;}\nstatic void play_vm_se_params','return blocks(x,y,id);}\nstatic void play_vm_se_params')
pre += '\nstatic uint8_t g_switches[1024];\nstatic int is_chase_enemy(int,int);\n'
contact=s[s.index("static int is_chase_enemy("):s.index("static int vm_find_event_at(")]
post=contact+"""static int blocks(int x,int y,int id){MapState m={94,12};for(int j=1;j<13;j++)if(j!=id&&priorities[j]==1&&!(flags[j]&1)){VmEventRecord ev={j,coords[j][0],coords[j][1],0};int cx,cy;vm_event_contact_cell(&m,&ev,&cx,&cy);if(cx==x&&cy==y)return 1;}return 0;}
static void frames(MapState*m,int n){for(int f=0;f<n;f++)tick_event_routes(m);}
int main(void){MapState m={94,12};for(int j=1;j<13;j++){g_event_shift_x[j]=g_event_shift_y[j]=0;g_event_active_page[j]=-1;}priorities[11]=priorities[12]=0;
"""
sys.path.insert(0,str(r/'tools'));import prepare_world_v060 as w
pg=m['events'][9]['pages'][0]
for ci,c in enumerate(pg['list']):
 if c['code']==121 and c['parameters'][0]==926:post+='priorities[11]=priorities[12]=1;\n'
 if c['code'] in (101,230,204):post+=f'frames(&m,{c["parameters"][0] if c["code"]==230 else 120});\n'
 if c['code']!=205:continue
 eid=c['parameters'][0]
 if eid<0:
  post+=f'frames(&m,{max(1,len(c["parameters"][1]["list"])*8)});\n';continue
 cmd=w.compile_vm_commands({'list':[c,{'code':0,'indent':0,'parameters':[]}]},{})
 eid,n,fl=struct.unpack_from('<hHB',cmd,1);raw=cmd[6:6+n*5];post+=f'uint8_t r{ci}[]={{{",".join(map(str,raw))}}};start_event_route(&m,{eid},r{ci},{n},{fl});\n'
 if fl&4:post+=f'{{int f;for(f=0;f<3000&&g_routes[{eid}].records;f++)tick_event_routes(&m);if(g_routes[{eid}].records){{printf("BLOCK command {ci} event {eid} at %f,%f index %d\\n",coords[{eid}][0]+g_event_shift_x[{eid}],coords[{eid}][1]+g_event_shift_y[{eid}],g_routes[{eid}].index);return 1;}}}}\n'
post+='puts("All NPC routes complete");return 0;}'
Path('/tmp/replay162.c').write_text(pre+glob+body+post);subprocess.run(['cc','-std=c99','-I',str(r),'/tmp/replay162.c','-o','/tmp/replay162'],check=True);subprocess.run(['/tmp/replay162'],check=True)
