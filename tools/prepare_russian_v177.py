"""Build an additive Russian dictionary; never rewrite existing language assets."""
import json,re,struct,sys
from pathlib import Path
import prepare_world_v060 as w
from update_window_styles_v174 import decode
ROOT=Path(__file__).resolve().parents[1]
def norm(s):
 s=re.sub(r'\\(?:[a-zA-Z]+\[[^\]]*\]|[^a-zA-Z])','',s)
 return ''.join(c.lower() if 'A'<=c<='Z' else c for c in s if c not in ' \t\r\n\u3000')
def load_translations():
 source=json.loads((ROOT/'tools/ru_source.json').read_text())
 out={}
 for line in (ROOT/'tools/ru_translation.tsv').read_text().splitlines():
  i,t=line.split('\t',1);i=int(i)
  assert i not in out
  out[i]=t.replace('\\n','\n')
 assert set(out)==set(range(len(source)))
 return dict(zip(source,(out[i]for i in range(len(source)))))
def vm_strings(b):
 for a,z,op,kind in decode(b):
  p=a+1+(2 if op in(44,45)else 0)
  if kind==1:
   lens=struct.unpack_from('<8H',b,p);q=p+16
   yield b[q:q+lens[0]].decode();yield b[q+lens[0]:q+lens[0]+lens[1]].decode()
  elif kind==22:
   n=b[p];p+=3
   for i in range(n):
    lens=struct.unpack_from('<4H',b,p);p+=8
    yield b[p:p+lens[0]].decode();p+=sum(lens)
  elif kind==43:
   lens=struct.unpack_from('<4H',b,p+2);q=p+10
   yield b[q:q+lens[0]].decode()
def installed_strings():
 for f in sorted((ROOT/'assets').glob('*_vm.bin')):
  b=f.read_bytes()
  if b[:4]==b'NV40':
   _,ne,np,blob,_,_=struct.unpack_from('<4sHHIII',b)
   for i in range(np):
    off,size=struct.unpack_from('<II',b,20+ne*10+i*20+12)
    if size:yield from vm_strings(b[blob+off:blob+off+size])
  elif b[:4]==b'NC50':
   n=struct.unpack_from('<H',b,4)[0]
   for i in range(n):
    off,size=struct.unpack_from('<II',b,8+i*8)
    if size:yield from vm_strings(b[off:off+size])
def main(game):
 trans=load_translations();texts=w.read_json(game/'data/I18NTexts.json')
 ru=[]
 for x in texts:
  d=dict(x)if isinstance(x,dict)else{}
  d['ru_RU']=trans.get(d.get('en_US',''),'');ru.append(d)
 # The original labels these two green pickups as iron in English. Match the port fix.
 for i in(1308,1329):ru[i]['ru_RU']='Получен \\c[3]Зелёный ключ\\c[0].'
 table={}
 def add(en,russian):
  key=norm(en)
  if key and russian:table[key]=russian
 def localized(raw):return w.localized_string(raw,ru,'ru_RU')
 def add_raw(raw):add(w.localized_string(raw,texts,'en_US'),localized(raw))
 for en,t in trans.items():add(en,t)
 def commands(lst):
  for i,c in enumerate(lst):
   code=c.get('code');p=c.get('parameters',[])
   if code in(101,105):
    if code==101 and len(p)>4:add_raw(p[4])
    lines=[];j=i+1
    while j<len(lst)and lst[j].get('code')==(401 if code==101 else 405):lines.append(lst[j]['parameters'][0]);j+=1
    en='\n'.join(w.localized_string(x,texts,'en_US')for x in lines)
    vals=[localized(x)for x in lines]
    # Caption and scrolling lines are authored rows. Ordinary prose is reflowed on PSP.
    rr=('\n'if code==105 or norm(en).startswith('end')else ' ').join(vals)
    add(en,rr)
   elif code==102:
    for x in p[0]:add_raw(x)
 for f in sorted((game/'data').glob('Map[0-9][0-9][0-9].json')):
  for e in w.read_json(f)['events']:
   if e:
    for pg in e['pages']:commands(pg['list'])
 for c in w.read_json(game/'data/CommonEvents.json'):
  if c:commands(c['list'])
 for it in w.read_json(game/'data/Items.json'):
  if it:add_raw(it.get('name',''));add_raw(it.get('description',''))
 table.update({norm(k):v for k,v in {'ON':'ВКЛ','OFF':'ВЫКЛ','Empty':'Пусто','Shutdown':'Выход','Language':'Язык'}.items()})
 # Audit the actual shipped messages, including corrections made after extraction.
 missing=sorted({x for x in installed_strings()if norm(x)and norm(x)not in table})
 (ROOT/'tools/ru_unmatched.json').write_text(json.dumps(missing,ensure_ascii=False,indent=2))
 assert not missing, 'Untranslated installed messages: see ru_unmatched.json'
 (ROOT/'tools/ru_dictionary.json').write_text(json.dumps(table,ensure_ascii=False,indent=2))
 print('dictionary',len(table),'unmatched',len(missing))
if __name__=='__main__':main(Path(sys.argv[1]))
