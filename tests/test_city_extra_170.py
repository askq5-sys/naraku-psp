from pathlib import Path
import sys,struct
from PIL import Image
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'tools'));import prepare_world_v060 as w
G=r.parent/'original';key=bytes.fromhex(w.read_json(G/'data/System.json')['encryptionKey'])
for mid in (*range(80,105),*range(111,140)):
 original=w.read_json(G/'data'/f'Map{mid:03}.json')
 assert w.adapt_stage_152(original,mid)['events']==original['events'],mid
for aid in (7,8,9,10):
 actor=w.read_json(G/'data/Actors.json')[aid];source=w.load_encrypted_png(w.resolve_named_file(G/'img/characters',actor['characterName']),key)
 atlas=Image.frombytes('RGBA',(256,512),(r/'assets'/f'actor{aid:02}_atlas.rgba8888').read_bytes())
 for row in range(4):
  for pat in range(3):
   f=w.extract_character_frame(source,actor['characterName'],actor['characterIndex'],2+row*2,pat);expected=Image.new('RGBA',f.size);expected.alpha_composite(f)
   x,y=pat*50+1,row*80+1
   assert f.size==(48,78)and atlas.crop((x,y,x+48,y+78)).tobytes()==expected.tobytes(),(aid,row,pat)
mp=w.read_json(G/'data/Map120.json');route=mp['events'][6]['pages'][0]['moveRoute']
cmd=w.compile_vm_commands({'list':[{'code':205,'indent':0,'parameters':[6,route]}]},{});eid,n,flags=struct.unpack_from('<hHB',cmd,1)
s=(r/'runtime/factory_routes.h').read_text();import re
actual=bytes(map(int,re.search(r'factory_route_120_6_0\[\]=\{([^}]+)',s)[1].split(',')))
assert actual==cmd[6:6+n*5]and flags==3 and n==8
print('PASS: no remaining city boundary guards; all 48 native alternate Will frames preserved; original rotating NPC route included')
