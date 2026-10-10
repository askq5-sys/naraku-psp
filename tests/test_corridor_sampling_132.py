"""Verify stable prefiltered PSP texel grids without changing map/event logic."""
from pathlib import Path
import json,sys,struct,zipfile
from PIL import Image
import numpy as np
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'tools'));import prepare_world_v060 as w
G=r.parent/'original';O=r/'assets';key=bytes.fromhex(json.load(open(G/'data/System.json'))['encryptionKey']);ts=json.load(open(G/'data/Tilesets.json'))
count=0
for mid in(33,34):
 m=json.load(open(G/'data'/f'Map{mid:03}.json'));sets=ts[m['tilesetId']];bitmaps={}
 for i,name in enumerate(sets['tilesetNames']):
  if name:bitmaps[i]=w.load_encrypted_png(w.resolve_named_file(G/'img/tilesets',name),key)
 atlas=Image.frombytes('RGBA',(512,512),(O/f'map{mid:03}_atlas0.rgba8888').read_bytes());ids=sorted(set(m['data'][:m['width']*m['height']*4])-{0})
 for i,tid in enumerate(ids):
  if tid in (355,356,357,363,364,365):continue
  x=i%10*50+1;y=i//10*50+1;actual=atlas.crop((x,y,x+48,y+48));a=np.array(actual)
  assert np.array_equal(a[0::2,0::2],a[1::2,0::2])and np.array_equal(a[0::2,0::2],a[0::2,1::2])and np.array_equal(a[0::2,0::2],a[1::2,1::2])
  tile=w.render_tile(tid,bitmaps).resize((24,24),Image.Resampling.LANCZOS).resize((48,48),Image.Resampling.NEAREST);normalized=Image.new('RGBA',(48,48));normalized.alpha_composite(tile);assert actual.tobytes()==normalized.tobytes();count+=1
 # Original scripts and passage metadata remain byte-identical to the delivered patch.
 for suffix in('_vm.bin',):
  assert (r.parent/'github_latest/menu133/assets'/f'map{mid:03}{suffix}').read_bytes()==(O/f'map{mid:03}{suffix}').read_bytes()

# Map layer flags may add filtering, but tile IDs and passage bytes stay unchanged.
 old=(r.parent/'github_latest/menu133/assets'/f'map{mid:03}.bin').read_bytes();new=(O/f'map{mid:03}.bin').read_bytes();n=m['width']*m['height']*4
 assert old[20+n*2:]==new[20+n*2:]
 for i in range(n):assert struct.unpack_from('<H',old,20+i*2)[0]&0xBFFF==struct.unpack_from('<H',new,20+i*2)[0]&0xBFFF

print(f'PASS: {count} background tiles retain fixed PSP sampling grids; corpse detail is checked in test_factory_graphics.py')
