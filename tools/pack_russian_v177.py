"""Package Russian text and append Cyrillic glyphs without changing old glyphs."""
import json,re,struct
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1]
def clean(s):
 s=re.sub(r'\\[fF][sS]\[\d+\]|\\[iI]\[\d+\]','',s)
 for c in ('.','|','!','>','<'):s=s.replace('\\'+c,'')
 return s

def pack():
 table=json.loads((R/'tools/ru_dictionary.json').read_text())
 table={k:clean(v)for k,v in table.items()}
 # Keep item emphasis in translated prose; single inventory labels remain plain.
 def colors(s):
  if '\\c['in s or len(s.split())<=2:return s
  for pat,color in [(r'(?i)\bзелён(?:ый|ого|ым|ом) ключ(?:а|ом|е)?\b',3),(r'(?i)\bкрасн(?:ый|ого|ым|ом) ключ(?:а|ом|е)?\b',18),(r'(?i)\bзолот(?:ой|ого|ым|ом) ключ(?:а|ом|е)?\b',14)]:
   s=re.sub(pat,lambda m:'\\c['+str(color)+']'+m.group()+'\\c[0]',s)
  return s
 table={k:colors(v)for k,v in table.items()}
 keys=sorted(table,key=lambda k:k.encode());h=bytearray(b'NR77'+struct.pack('<I',len(keys))+bytes(len(keys)*12));blob=bytearray()
 for i,k in enumerate(keys):
  ko=len(h)+len(blob);blob+=k.encode()+b'\0';vo=len(h)+len(blob);t=table[k].encode();blob+=t+b'\0';struct.pack_into('<III',h,8+i*12,ko,vo,len(t))
 (R/'assets/russian177.bin').write_bytes(h+blob)
 old=(R/'assets/font_map.bin').read_bytes();recs=[old[i:i+8]for i in range(12,len(old),8)];recs=[r for r in recs if r[4]!=7];have={struct.unpack_from('<I',r)[0]for r in recs}
 ui=(R/'main.c').read_text()
 chars={ord(c)for v in table.values()for c in v}|{ord(c)for c in ui if '\u0400'<=c<='\u052f'}
 missing=sorted(chars-have-{10,13,9});print('Additional glyphs',len(missing))
 assert len(missing)<=21*18
 # Page 7 is reserved for the additive Russian alphabet.
 canvas=Image.new('L',(512,512));draw=ImageDraw.Draw(canvas);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',18)
 for slot,cp in enumerate(missing):
  x=(slot%21)*24;y=(slot//21)*28;adv=min(24,max(12,int(font.getlength(chr(cp))+1)))
  draw.text((x,y),chr(cp),font=font,fill=255)
  recs.append(struct.pack('<IBHB',cp,7,slot,adv))
 recs.sort(key=lambda r:struct.unpack_from('<I',r)[0]);header=bytearray(old[:12]);struct.pack_into('<H',header,4,len(recs));header[6]=8
 (R/'assets/font_map.bin').write_bytes(header+b''.join(recs));(R/'assets/font_page7.t8').write_bytes(canvas.tobytes())
 # A separate Russian controls card keeps the user's existing four-language card.
 card=Image.new('RGBA',(512,512),(0,0,0,0));d=ImageDraw.Draw(card);d.rectangle((0,0,479,271),fill=(0,0,0,255));f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
 for y,t in enumerate(['Управление PSP','Крестовина — движение','X — действие, осмотреть','O — меню, отмена','R — бег']):d.text((16,16+y*27),t,font=f,fill='white')
 from prepare_ui_v060 import rgba4444_bytes
 (R/'assets/controls_ru177.p44').write_bytes(struct.pack('<4sHH',b'NP50',480,272)+rgba4444_bytes(card))
 print('Russian dictionary:',len(keys),'entries,',len(h+blob),'bytes')
if __name__=='__main__':pack()
