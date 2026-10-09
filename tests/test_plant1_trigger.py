from pathlib import Path
import json,struct,sys
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'tools'));import prepare_world_v060 as w
original=json.load(open(r.parent/'original/data/Map009.json'));before=json.dumps(original,sort_keys=True);data=w.adapt_plant1_worm(original)
assert json.dumps(original,sort_keys=True)==before
wall=data['events'][4];floor=data['events'][15];scene=floor['pages'][1]
assert (wall['x'],wall['y'])==(28,18)and(floor['x'],floor['y'])==(28,21)
assert wall['pages'][4]['image']==original['events'][4]['pages'][4]['image']
assert wall['pages'][4]['trigger']==0 and wall['pages'][4]['list']==[{'code':0,'indent':0,'parameters':[]}]
assert scene['trigger']==1 and scene['priorityType']==0 and scene['conditions']['switch1Id']==22
assert scene['list']==original['events'][4]['pages'][4]['list'][2:]
assert not any(c['code']==201 for c in scene['list'])
assert floor['pages'][0]==original['events'][15]['pages'][0]
for e in data['events']:
 if e and e['id']not in(4,15):assert e==original['events'][e['id']]
raw=(r/'assets/map009_vm.bin').read_bytes();_,ne,np,off,size,flags=struct.unpack_from('<4sHHIII',raw);pages=20+ne*10
for i in range(ne):
 eid,x,y,first,n,_=struct.unpack_from('<HHHHBB',raw,20+i*10)
 if eid==15:
  assert(x,y,n)==(28,21,2);p=pages+(first+1)*20
  assert raw[p+1]==1 and raw[p+2]==0 and raw[p+9]==1
  assert struct.unpack_from('<H',raw,p+4)[0]==22 and struct.unpack_from('<H',raw,p+10)[0]==0
print('PASS: third-tile trigger, switch 22 gate, unchanged flesh wall/footsteps/other events, no backwards transfer, original worm sequence retained')
