from pathlib import Path
import sys,tempfile,subprocess
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'tools'));import prepare_world_v060 as w
count=0;exceptions=[]
for p in sorted((r.parent/'original/data').glob('Map[0-9][0-9][0-9].json')):
 mid=int(p.stem[3:])
 for ev in w.read_json(p)['events']:
  if not ev:continue
  for j,pg in enumerate(ev['pages']):
   count+=1
   if not w.page_vm_supported(pg):exceptions.append((mid,ev['id'],j))
assert count==3543 and exceptions==[(32,20,1)]
s=(r/'main.c').read_text();a=s.index('static void tick_factory_parallel(');b=s.index('static void render_world(',a)
assert 'Original Set Event Location' in s[a:b] and 'g_event_shift_x[19]=g_event_shift_y[19]=0;'in s[a:b]
assert '(message_len>=4 && !memcmp(message,"END ",4))'in s
texts=w.read_json(r.parent/'original/data/I18NTexts.json');mp=w.read_json(r.parent/'original/data/Map082.json')
p=mp['events'][13]['pages'][4];cmd=p['list'];i=next(i for i,c in enumerate(cmd)if c['code']==401 and '2330'in str(c))
lines=[w.localized_string(cmd[j]['parameters'][0],texts,'en_US')for j in range(i-2,i+1)]
assert lines[0].startswith('END ')and'I see something'in lines[2]
pre='''#include <assert.h>
#include "runtime/render_boundaries.h"
int main(void){assert(secret_ladder_clip_top(114,14.5f*24,48,24,0,0,272)==24);
assert(secret_ladder_clip_top(114,14.5f*24,96,24,0,0,272)==-1);
assert(secret_ladder_clip_top(113,14.5f*24,48,24,0,0,272)==-1);
assert(secret_ladder_clip_top(105,2.5f*24,400,24,0,100,272)==272);
return 0;}'''
with tempfile.TemporaryDirectory()as td:
 p=Path(td)/'t.c';e=Path(td)/'t';p.write_text(pre);subprocess.run(['cc','-I',str(r),str(p),'-lm','-o',str(e)],check=True);subprocess.run([str(e)],check=True)
print('PASS: 3,543 original pages covered by compiler or existing factory scheduler; original separate ending lines; gallery clipping and ladder regression')
