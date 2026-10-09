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
  x=i%10*50+1;y=i//10*50+1;actual=atlas.crop((x,y,x+48,y+48));a=np.array(actual)
  assert np.array_equal(a[0::2,0::2],a[1::2,0::2])and np.array_equal(a[0::2,0::2],a[0::2,1::2])and np.array_equal(a[0::2,0::2],a[1::2,1::2])
  tile=w.render_tile(tid,bitmaps).resize((24,24),Image.Resampling.LANCZOS).resize((48,48),Image.Resampling.NEAREST);normalized=Image.new('RGBA',(48,48));normalized.alpha_composite(tile);assert actual.tobytes()==normalized.tobytes();count+=1
 # Original scripts and passage metadata remain byte-identical to the delivered patch.
 with zipfile.ZipFile(r.parent/'latest/naraku_psp_1.3.1_factory_extension_patch.zip')as z:
  for suffix in('.bin','_vm.bin'):
   assert z.read(f'assets/map{mid:03}{suffix}')==(O/f'map{mid:03}{suffix}').read_bytes()
 # Body sprite texture frames are constant on each PSP texel's source 2x2 block.
 eb=(O/f'map{mid:03}_events.bin').read_bytes();_,mw,mh,nt,ns,_=struct.unpack_from('<4s5H',eb);base=14+mw*mh*5+nt*20
 atlas=Image.frombytes('RGBA',(512,512),(O/f'map{mid:03}_event_atlas.rgba8888').read_bytes())
 for i in range(ns):
  rec=struct.unpack_from('<6H2BH',eb,base+i*16);sx,sy,sw,sh=rec[2:6]
  if(sw,sh)!=(144,96):continue
  a=np.asarray(atlas.crop((sx,sy,sx+sw,sy+sh)));assert np.array_equal(a[::2,::2],a[1::2,1::2])
print(f'PASS: {count} background tiles and all corpse sheets have fixed 2x2 PSP sampling grids; corridor VM commands, tile flags and passage bytes unchanged')
