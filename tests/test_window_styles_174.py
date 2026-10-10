from pathlib import Path
import sys,json,struct
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'tools'));import update_window_styles_v174 as u
meta=json.loads((r/'tools/window_styles_v174.json').read_text());counts=[0,0,0];n=0
for p in sorted((r/'assets').glob('map*_vm.bin')):
 b=p.read_bytes();ne,np,blob,bs=struct.unpack_from('<HHII',b,4);base=20+ne*10;mid=str(int(p.name[3:6]))
 assert u.update_vm(p,meta[mid])==b # Idempotent installation.
 for i in range(ne):
  eid,x,y,first,pages,_=struct.unpack_from('<HHHHBB',b,20+i*10)
  for j in range(pages):
   at=base+(first+j)*20;off,size=struct.unpack_from('<II',b,at+12);code=b[blob+off:blob+off+size];records=u.decode(code)
   windows=[a for a,z,op,kind in records if kind in(1,22)]
   if not windows:continue
   for a,(_,bg,pos)in zip(windows,meta[mid][f'{eid}:{j}']):
    assert code[a]in(44,45)and code[a+1:a+3]==bytes((bg,pos));counts[bg]+=1;n+=1
   starts={a for a,z,op,kind in records}|{len(code)}
   for a,z,op,kind in records:
    if op in u.JUMPS:assert struct.unpack_from('<I',code,a+1+u.JUMPS[op])[0]in starts
assert all(counts)
# Explicit caption must be transparent and middle-positioned.
assert [101,2,1]in meta['82']['13:4']
print(f'PASS: {n} source window modes/positions; normal/dim/transparent={counts}; all relocated branches valid; migration idempotent')
