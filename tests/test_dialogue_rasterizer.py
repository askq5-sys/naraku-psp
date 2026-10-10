from pathlib import Path
import runpy,subprocess,tempfile,json
r=Path(__file__).resolve().parents[1];s=(r/'main.c').read_text()
n=runpy.run_path(str(r/'tests/test_flashback_text.py'))
pre=n['pre'].split('static void vm_wait_text_page(')[0]
a=s.index('static int latin_word_cp(');b=s.index('static int latin_word_width(',a)
pre+=s[a:b]+'''static int drawn,last_y;
static int parse_text_color_escape(const char**p,const char*end,int*c){return 0;}
static void rasterize_glyph_to_message_surface(uint32_t cp,int x,int y,int color,float scale){assert(x>=119&&x<361);drawn++;last_y=y;}
'''
a=s.index('static int message_word_width(');b=s.index('/* Original ITB_ResizeMessageWindow',a);pre+=s[a:b]
pre+='''static int expected_lines;
static void vm_wait_text_page(const MapState*m,void*a,int x,int y,int d,const char*sp,size_t sl,const char*t,size_t len,int next){
int expected=0;const char*p=t,*end=t+len;while(p<end){unsigned cp=utf8_next_cp(&p,end);if(cp!=' '&&cp!='\\n'&&cp!='\\r'&&cp!='\\t')expected++;}
drawn=last_y=0;rasterize_utf8_wrapped_to_message_surface(t,len,119,0,361,3,.55f);assert(drawn==expected);assert(last_y/14+1<=expected_lines);}
'''
a=s.index('static char *strip_message_font_controls(');b=s.index('static void vm_pump_stage_message(',a)
post='int main(int argc,char**argv){FILE*f=fopen(argv[1],"rb");font_size=fread(font,1,sizeof(font),f);fclose(f);MapState m={24};'
cases=[(2,"It seems one more key is required to open\nthe shutter."),(2,"Hey, hey! Oh, Enriii! So like, I've got a\nlittle favor to ask..."),(3,"So would you mind taking these materials and\nstuff to Mrs. Peliah in the teacher's lounge?"),(3,"Oof, y'know, these are too heavy to wait for\nan answer!\nYou take care of the rest, Enri! ♪")]
for lines,t in cases:post+=f'expected_lines={lines};vm_wait_text(&m,NULL,0,0,0,"",0,'+json.dumps(t,ensure_ascii=False)+f',{len(t.encode())},0);'
post+='return 0;}'
with tempfile.TemporaryDirectory()as tmp:
 p=Path(tmp)/'t.c';e=Path(tmp)/'t';p.write_text(pre+s[a:b]+post);subprocess.run(['cc',str(p),'-o',str(e)],check=True);subprocess.run([str(e),str(r/'assets/font_map.bin')],check=True)
print('PASS: actual dialogue rasterizer retains every glyph; shutter/Emma fit two lines, materials/heavy messages fit three')
