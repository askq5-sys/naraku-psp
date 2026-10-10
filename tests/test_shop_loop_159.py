from pathlib import Path
import sys,struct
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'tools'))
import prepare_world_v060 as w
page={'list':[{'code':112,'indent':0,'parameters':[]},{'code':113,'indent':1,'parameters':[]},{'code':413,'indent':0,'parameters':[]}]}
assert w.page_vm_supported(page)
b=w.compile_vm_commands(page,[])
assert b==bytes([20])+struct.pack('<I',10)+bytes([20])+struct.pack('<I',0)+bytes([0])
# The nearest nested loop owns the break; outer loop still repeats.
page={'list':[{'code':112,'indent':0,'parameters':[]},{'code':112,'indent':1,'parameters':[]},{'code':113,'indent':2,'parameters':[]},{'code':413,'indent':1,'parameters':[]},{'code':413,'indent':0,'parameters':[]}]}
b=w.compile_vm_commands(page,[])
assert struct.unpack_from('<I',b,1)[0]==10 and struct.unpack_from('<I',b,11)[0]==0
print('PASS: shop break exits the nearest loop and preserves enclosing repeat')
