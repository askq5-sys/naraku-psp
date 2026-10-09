"""Audit compiled pages/resources and exercise the requested puzzle branches."""
from pathlib import Path
import json,struct,sys,re,collections
from PIL import Image
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'tools'));import prepare_world_v060 as w
G=r.parent/'original';O=r/'assets';texts=json.load(open(G/'data/I18NTexts.json'));key=bytes.fromhex(json.load(open(G/'data/System.json'))['encryptionKey'])
w.PICTURE_IDS=json.load(open(O/'picture_v050_manifest.json'));audio=json.load(open(O/'audio_exact_v079.json'));w.EXACT_SE_IDS={w.audio_key(x):x['id']for x in audio if x['kind']=='se'};w.EXACT_BGM_IDS={w.audio_key(x):x['id']for x in audio if x['kind']=='bgm'}
import zipfile
with zipfile.ZipFile(r.parent/'latest/naraku_psp_1.3.1_factory_extension_patch.zip')as z:old=json.loads(z.read('assets/audio_exact_v079.json'));assert all(row in audio for row in old)
report=[];pages={};sprites=0;frames=0
for mid in range(36,46):
 m=json.load(open(G/'data'/f'Map{mid:03}.json'));b=(O/f'map{mid:03}_vm.bin').read_bytes();_,ne,np,blob,_,flags=struct.unpack_from('<4sHHIII',b);assert flags&1;base=20+ne*10
 mb=(O/f'map{mid:03}.bin').read_bytes();tileset=json.load(open(G/'data/Tilesets.json'))[m['tilesetId']];mw,mh=m['width'],m['height']
 for y in range(mh):
  for x in range(mw):assert mb[20+mw*mh*8+y*mw+x]==w.build_pass_mask(m,tileset['flags'],x,y)
 eb=(O/f'map{mid:03}_events.bin').read_bytes();_,mw,mh,nt,ns,_=struct.unpack_from('<4s5H',eb);sb=14+mw*mh*5+nt*20
 atlases=[Image.frombytes('RGBA',(512,512),(O/f'map{mid:03}_event_atlas.rgba8888').read_bytes())]
 if mid in(39,40):atlases.append(Image.frombytes('RGBA',(512,512),(O/f'map{mid:03}_event_atlas1.rgba8888').read_bytes()))
 for i in range(ne):
  eid,x,y,first,n,_=struct.unpack_from('<HHHHBB',b,20+i*10);ev=m['events'][eid];assert(x,y,n)==(ev['x'],ev['y'],len(ev['pages']))
  for j,p in enumerate(ev['pages']):
   pg=struct.unpack_from('<BBBBHHBBHII',b,base+(first+j)*20);ref,off,length=pg[8:];assert pg[7]and w.page_vm_supported(p)
   data=b[blob+off:blob+off+length];assert data==w.compile_vm_commands(p,texts);pages[mid,eid,j]=data
   assert (pg[0],pg[4],pg[5],pg[6])==w.vm_page_conditions(p);assert pg[1]==p['trigger']and pg[2]==p['priorityType']and bool(pg[3]&1)==p['through']
   img=p['image'];name=img['characterName'];assert bool(ref)==bool(name or img['tileId'])
   if ref:
    sprites+=1;rec=struct.unpack_from('<6H2BH',eb,sb+(ref-1)*16);assert rec[-1]==eid;sx,sy,sw,sh=rec[2:6];atlas=atlases[sx>>12];sx&=0xFFF;flags2=rec[7]
    if name and name!='お邪魔ブロック！！':
     assert flags2&4;src=w.load_encrypted_png(w.resolve_named_file(G/'img/characters',name),key)
     dirs=(2,4,6,8)if flags2&64 else(img['direction'],);patterns=range(3)if flags2&130 else(img['pattern'],)
     for di,d in enumerate(dirs):
      for pat in patterns:
       frame=w.extract_character_frame(src,name,img['characterIndex'],d,pat)
       if name in('!クランク','!吊るしエンリ')or name=='S-003':frame=frame.resize((frame.width*3//4,frame.height*3//4),Image.Resampling.LANCZOS)
       assert frame.size==(sw,sh)
       xx=sx;yy=sy
       if flags2&64:
        if flags2&128:xx+=(di%2*3+pat)*sw;yy+=di//2*sh
        elif mid==43:xx+=di%2*sw;yy+=di//2*sh
        else:yy+=di*sh
       elif flags2&2:xx+=pat*sw
       assert xx+sw<=512 and yy+sh<=512
       expected=Image.new('RGBA',frame.size);expected.alpha_composite(frame)
       assert atlas.crop((xx,yy,xx+sw,yy+sh)).tobytes()==expected.tobytes(),(mid,eid,j,d,pat);frames+=1
   for c in p['list']:
    if c['code']==231 and c['parameters'][1]!='A1':assert(O/f"pic_{w.PICTURE_IDS[c['parameters'][1]]:03}.p44").is_file()
    if c['code']in(241,250)and c['parameters'][0]['name']:
     kind='bgm'if c['code']==241 else'se';ids=w.EXACT_BGM_IDS if kind=='bgm'else w.EXACT_SE_IDS;assert(O/f'{kind}_exact_{ids[w.audio_key(c["parameters"][0])]}.pcm').stat().st_size>0
 report.append({'map':mid,'pages':np,'compiled':np})
# Bytecode branch simulator. Each payload comes from the actual packed VM.
def run(mid,eid,page,choice=0,items=None,switches=None,number=0):
 b=pages[mid,eid,page];p=0;sw=collections.defaultdict(int,switches or{});it=collections.defaultdict(int,items or{});var=collections.defaultdict(int);trace=[];visible=1
 def read(fmt):
  nonlocal p
  out=struct.unpack_from(fmt,b,p);p+=struct.calcsize(fmt);return out
 while p<len(b):
  op=b[p];p+=1
  if op==0:break
  if op==1:
   lengths=read('<8H');p+=sum(lengths)
  elif op==2:
   a,z,v=read('<HHB')
   for k in range(a,z+1):sw[k]=v
   trace.append(('switch',a,z,v))
  elif op==4:trace.append(('wait',read('<H')[0]))
  elif op==5:trace.append(('transfer',*read('<HHHBB')))
  elif op in(6,11):trace.append(('sound',*read('<HBBB')))
  elif op==7:
   i,n=read('<Hh');it[i]=max(0,it[i]+n)
  elif op==8:visible=read('<B')[0]
  elif op==16:
   i,v,to=read('<HBI')
   if sw[i]!=v:p=to
  elif op==17:
   i,operator,value,to=read('<HBiI');actual=var[i]
   if not [actual==value,actual>=value,actual<=value,actual>value,actual<value,actual!=value][operator]:p=to
  elif op==18:
   i,to=read('<HI')
   if not it[i]:p=to
  elif op==20:p=read('<I')[0]
  elif op==22:
   n,_,_=read('<BBB')
   for _ in range(n):
    lengths=read('<4H');p+=sum(lengths)
  elif op==23:
   idx,to=read('<BI')
   if idx!=choice:p=to
  elif op==30:p+=5
  elif op==34:
   target,n,flags=read('<hHB');trace.append(('route',target,tuple(read('<Bhh')for _ in range(n))))
  elif op==37:trace.append(('fade',read('<B')[0]))
  elif op==38:
   i,d=read('<HB');assert d==4;var[i]=number
  else:raise AssertionError((mid,eid,op,p))
 return sw,it,trace,visible
# Metal sheets: bare hands cannot open, axe does and is consumed; leave does neither.
sw,it,tr,vis=run(37,3,0,choice=0);assert not sw[291]and vis==1 and any(t[0]=='route'for t in tr)
sw,it,tr,vis=run(37,3,0,choice=1,items={54:1});assert sw[291]and sw[293]and not it[54]and vis==1
for idx in(0,2):
 sw,it,tr,vis=run(37,3,0,choice=idx,items={54:1});assert not sw[291]and it[54]==1 and vis==1
# Crank both directions and return neutral. Leave changes nothing.
for idx,last in((0,342),(1,343)):
 sw,it,tr,_=run(40,4,1,choice=idx,switches={334:1});assert sw[335]and not sw[334]and sw[341]and sw[last]
sw,it,tr,_=run(40,4,1,choice=2,switches={334:1});assert sw[334]and not sw[335]
sw,it,tr,_=run(40,4,2,choice=0,switches={335:1,341:1,342:1,343:1});assert sw[334]and not any(sw[i]for i in(335,341,342,343))
# Collection hides page and grants exactly one item. Empty collected page does nothing.
sw,it,tr,_=run(43,12,0);assert sw[345]and it[50]==1
sw2,it2,tr,_=run(43,12,1,switches=sw,items=it);assert it2[50]==1 and sw2[345]
# Fade stays out over sound/wait/transfer and comes back in; refusing stays here.
sw,it,tr,_=run(36,15,0,choice=0);assert [t for t in tr if t[0]=='fade']==[('fade',1),('fade',0)];assert next(t for t in tr if t[0]=='transfer')[1]==37
sw,it,tr,_=run(36,15,0,choice=1);assert not any(t[0]in('fade','transfer')for t in tr)
for eid,correct,gate in((7,8888,370),(8,8465,371)):
 sw,it,tr,_=run(45,eid,0,number=correct);assert sw[gate]and any(t[0]=='route'for t in tr)
 sw,it,tr,_=run(45,eid,0,number=0);assert not sw[gate]and not any(t[0]=='route'for t in tr)
# Sensor routes and post-pickup page selection retain exact original switch gates.
h=(r/'runtime/factory_routes.h').read_text();m=json.load(open(G/'data/Map043.json'))
for eid,j in((5,0),(8,1)):
 p=m['events'][eid]['pages'][j];data=bytes(map(int,re.search(f'factory_route_43_{eid}_{j}'+r'\[\] = \{([^}]+)',h)[1].split(',')));assert data==b''.join(struct.pack('<Bhh',c['code'],0,0)for c in p['moveRoute']['list']if c['code'])
(r/'audit_factory_131.json').write_text(json.dumps({'maps':report,'pages':sum(x['pages']for x in report),'visible_pages':sprites,'source_frames_checked':frames},indent=2))
print(f'PASS: {sum(x["pages"]for x in report)} original pages, {sprites} visual pages, {frames} exact/filtered source frames, stable audio/pictures; sheet/crank/key/fade/password branches')
