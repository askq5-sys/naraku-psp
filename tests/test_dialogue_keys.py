from pathlib import Path
import subprocess,tempfile
r=Path(__file__).resolve().parents[1];s=(r/'main.c').read_text();a=s.index('static char *style_green_key_dialogue(');b=s.index('static void vm_wait_text_page(',a)
pre=r'''#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
static int latin_word_cp(unsigned c){return (c>='a'&&c<='z')||(c>='A'&&c<='Z');}
static int parse_text_color_escape(const char**p,const char*end,int*color){int n=0,used=0;if(end-*p>4&&sscanf(*p,"\\c[%d]%n",&n,&used)==1&&used){*p+=used;*color=n;return 1;}return 0;}
'''
post=r'''static void check(const char*t,const char*expected){size_t n;char*p=style_green_key_dialogue(t,strlen(t),&n);assert(p&&n==strlen(expected)&&!strcmp(p,expected));free(p);}
int main(void){
check("Obtained the \\c[18]Cleaver\\c[0].", "Obtained the \\c[18]Cleaver\\c[0].");
check("Obtained an Iron Key.", "Obtained an Iron Key.");
check("Iron Key opens it. The Iron key is here.", "Iron Key opens it. The Iron key is here.");
check("Obtained a Red Key.", "Obtained a \\c[18]Red Key\\c[0].");
check("Red key! A Green Key.", "\\c[18]Red key\\c[0]! A \\c[3]Green Key\\c[0].");
check("\\c[5]The Red Key\\c[0].", "\\c[5]The \\c[18]Red Key\\c[5]\\c[0].");
check("Obtained a Gold Key.", "Obtained a \\c[14]Gold Key\\c[0].");
check("Used the gold key.", "Used the \\c[14]gold key\\c[0].");return 0;}

'''
# Raw Python string uses two backslashes for a C string's one literal backslash.
with tempfile.TemporaryDirectory()as tmp:
 p=Path(tmp)/'t.c';e=Path(tmp)/'t';p.write_text(pre+s[a:b]+post);subprocess.run(['cc',str(p),'-o',str(e)],check=True);subprocess.run([str(e)],check=True)
raw=(r/'assets/map012_vm.bin').read_bytes();assert b'thesematerials'not in raw and b'towait'not in raw;assert b"things \nto do"not in raw
assert 'm->id != 12' not in s[s.index('static void vm_wait_text(\n'):s.index('static int vm_wait_choices(')]
print('PASS: original capitalization, red/green/gold colors, surrounding color restoration, normalized PC wraps and transfer-independent reflow')

assert 'message = "Obtained an \\\\c[8]Axe\\\\c[0].";' in (r/"main.c").read_text()
