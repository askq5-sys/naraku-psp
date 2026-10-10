"""Add original window metadata without changing installed commands or sprites."""
import json,struct,sys
from pathlib import Path
FIXED={0:0,2:5,3:2,4:2,5:8,6:5,7:4,8:1,9:11,10:11,11:5,12:2,13:0,14:1,15:9,16:7,17:11,18:6,19:5,20:4,23:5,24:2,25:16,26:17,27:2,28:1,29:4,30:5,31:0,32:21,33:22,35:0,36:1,37:1,38:3,39:1,41:2,42:4}
JUMPS={16:3,17:7,18:2,19:1,20:0,23:1}
def decode(b):
 p=0;result=[]
 while p<len(b):
  a=p;op=b[p];p+=1
  if op in(44,45):p+=2
  kind=1 if op in(1,40,44)else 22 if op in(22,45)else op
  if kind==1:p+=16+sum(struct.unpack_from('<8H',b,p))
  elif kind==22:
   n=b[p];p+=3
   for _ in range(n):lengths=struct.unpack_from('<4H',b,p);p+=8+sum(lengths)
  elif kind in(21,34):n=struct.unpack_from('<H',b,p+2)[0];p+=(5 if kind==34 else 4)+n*5
  elif kind==43:p+=10+sum(struct.unpack_from('<4H',b,p+2))
  else:p+=FIXED[kind]
  if p>len(b):raise ValueError('Truncated bytecode')
  result.append((a,p,op,kind))
 return result

def convert(b,modes):
 records=decode(b);expected=[x for x in records if x[3]in(1,22)]
 if len(expected)!=len(modes):raise ValueError(f'Window count mismatch {len(expected)} != {len(modes)}')
 offsets={};out=bytearray();patches=[];i=0
 for a,z,op,kind in records:
  offsets[a]=len(out);start=len(out)
  if kind in(1,22):
   code,bg,pos=modes[i];i+=1
   if code!=(101 if kind==1 else 102):raise ValueError('Window type mismatch')
   out+=bytes((44 if kind==1 else 45,bg,pos));out+=b[a+(3 if op in(44,45)else 1):z]
  else:
   out+=b[a:z]
   if op in JUMPS:patches.append((start+1+JUMPS[op],struct.unpack_from('<I',b,a+1+JUMPS[op])[0]))
 offsets[len(b)]=len(out)
 for at,target in patches:struct.pack_into('<I',out,at,offsets[target])
 decode(out)
 return bytes(out)

def update_vm(path,meta):
 b=path.read_bytes();magic,ne,np,blob,bs,flags=struct.unpack_from('<4sHHIII',b)
 if magic!=b'NV40':raise ValueError(path)
 base=20+ne*10;header=bytearray(b[:blob]);out=bytearray()
 for i in range(ne):
  eid,x,y,first,n,_=struct.unpack_from('<HHHHBB',b,20+i*10)
  for j in range(n):
   at=base+(first+j)*20;off,size=struct.unpack_from('<II',b,at+12);old=b[blob+off:blob+off+size]
   modes=meta.get(f'{eid}:{j}',[])
   new=convert(old,modes)if b[at+9] and old!=b'\0'else old
   struct.pack_into('<II',header,at+12,len(out),len(new));out+=new
 struct.pack_into('<I',header,12,len(out));return bytes(header+out)

def main(root):
 meta=json.loads((Path(__file__).with_name('window_styles_v174.json')).read_text());pending=[]
 for path in sorted(root.glob('map*_vm.bin')):
  key=str(int(path.name[3:6]))
  if key in meta:pending.append((path,update_vm(path,meta[key])))
 common=root/'common_vm.bin'
 if common.exists():
  b=common.read_bytes();magic,count,_=struct.unpack_from('<4sHH',b)
  if magic!=b'NC50':raise ValueError('Invalid common events')
  out=bytearray(b[:8+count*8]);blob=bytearray()
  for i in range(count):
   off,size=struct.unpack_from('<II',b,8+i*8)
   if not size:continue
   code=convert(b[off:off+size],meta['_common'].get(str(i),[]))
   struct.pack_into('<II',out,8+i*8,len(out)+len(blob),len(code));blob+=code
  pending.append((common,bytes(out+blob)))
 # Validate every file before replacing any installed resource.
 for path,b in pending:
  temp=path.with_suffix('.window174.tmp');temp.write_bytes(b);temp.replace(path)
 print(f'Original window styles applied to {len(pending)} installed maps')
if __name__=='__main__':main(Path(sys.argv[1]))
