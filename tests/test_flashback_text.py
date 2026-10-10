from pathlib import Path
import json,re,subprocess,tempfile
root=Path(__file__).resolve().parents[1];s=(root/'main.c').read_text()
a=s.index('static char *strip_message_font_controls(');b=s.index('static void vm_pump_stage_message(',a)
pre=r'''#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
#define MESSAGE_BOX_W 260
typedef struct {int id;} MapState;
static int g_language=0,pages,total;
static unsigned char font[65536];static size_t font_size;
static const uint8_t *font_find_glyph(uint32_t cp){for(size_t j=12;j+8<=font_size;j+=8){uint32_t c=font[j]|font[j+1]<<8|font[j+2]<<16|font[j+3]<<24;if(c==cp)return font+j;}return NULL;}
static uint32_t utf8_next_cp(const char **p,const char *end){unsigned char c=*(*p)++;if(c<128)return c;int n=c<224?1:c<240?2:3;uint32_t v=c&((1<<(6-n))-1);while(n--&&*p<end)v=(v<<6)|(*(*p)++&63);return v;}
static void vm_wait_text_page(const MapState*m,void*a,int x,int y,int d,const char*sp,size_t sl,const char*t,size_t len,int next){
int lines=1,width=0;const char*p=t,*end=t+len;pages++;
while(p<end){uint32_t c=utf8_next_cp(&p,end);if(c=='\n'){assert(width<=242);width=0;lines++;continue;}const uint8_t*r=font_find_glyph(c);width+=r?(int)(r[7]*.55f):5;if(c!=' '&&c!='\r'&&c!='\t')total++;}assert(width<=242&&lines<=3);}
'''.replace("c=='\\n'","c=='\n'").replace("c!='\\r'","c!='\r'").replace("c!='\\t'","c!='\t'")
# Correct the C escape literals without converting them to actual line breaks.
pre=pre.replace("c=='\n'", "c=='\\n'").replace("c!='\r'", "c!='\\r'").replace("c!='\t'", "c!='\\t'")
texts=json.load(open(root.parent/'original/data/I18NTexts.json'));m=json.load(open(root.parent/'original/data/Map012.json'));cases=[]
for ev in m['events']:
 if not ev:continue
 for pg in ev['pages']:
  buf=[]
  for cmd in pg['list']:
   if cmd['code']==401:
    val=cmd['parameters'][0];val=re.sub(r'\\I18N\[(\d+)\]',lambda match:texts[int(match[1])]['en_US'],val);buf.append(val)
   elif buf:cases.append('\n'.join(buf));buf=[]
post='int main(int argc,char**argv){FILE*f=fopen(argv[1],"rb");assert(f);font_size=fread(font,1,sizeof(font),f);fclose(f);MapState m={12};'
for t in cases:
 expected=sum(not c.isspace()for c in t)
 post+='total=0;vm_wait_text(&m,NULL,0,0,0,"Emma",4,'+json.dumps(t,ensure_ascii=False)+','+str(len(t.encode()))+',0);assert(total=='+str(expected)+');'
post+='return 0;}'
with tempfile.TemporaryDirectory()as tmp:
 p=Path(tmp)/'t.c';e=Path(tmp)/'t';p.write_text(pre+s[a:b]+post);subprocess.run(['cc',str(p),'-o',str(e)],check=True);subprocess.run([str(e),str(root/'assets/font_map.bin')],check=True)
print(f'PASS: {len(cases)} original flashback messages fit in 3-row pages without losing text')
