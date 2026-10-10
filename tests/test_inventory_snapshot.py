"""Compare cached categories against the previous per-frame inventory collector."""
from pathlib import Path
import subprocess, tempfile
root = Path(__file__).resolve().parents[1]
old = (root / 'tests/inventory_collector_reference.inc').read_text()
a = old.index('static int ui_collect_owned_items(')
b = old.index('/* Compact inventory labels', a)
new = (root / 'runtime/inventory.inc').read_text()
c = new.index('typedef struct {')
d = new.index('/* Compact inventory labels', c)
source = r'''
#include <assert.h>
#include <stdint.h>
#include <string.h>
#define MAX_ITEMS 128
static struct { int item_count; } g_ui;
static int g_items[MAX_ITEMS],g_language,calls;
static char names[MAX_ITEMS][4], descriptions[MAX_ITEMS][4];
static int ui_item_text(int id,int lang,const char **n,size_t *nl,const char **d,size_t *dl,int *icon,int *type,int *occasion){
 ++calls;if(id%11==0)return 0;
 *n=names[id];*nl=lang+1;*d=descriptions[id];*dl=lang;
 *icon=id;*type=id%4;*occasion=0;return 1;
}
''' + old[a:b] + new[c:d] + r'''
int main(void){
 InventorySnapshot cached;int lang,category,ids[MAX_ITEMS],i,n;
 g_ui.item_count=MAX_ITEMS+17;
 for(i=0;i<MAX_ITEMS;i++)g_items[i]=(i%5)-1;
 for(lang=0;lang<4;lang++){
  g_language=lang;calls=0;ui_inventory_snapshot(&cached);
  assert(calls<=MAX_ITEMS-1);
  for(category=0;category<2;category++){
   n=ui_collect_owned_items(category,ids,MAX_ITEMS);assert(n==cached.count[category]);
   for(i=0;i<n;i++){
    InventoryEntry *e=&cached.entries[category][i];int id=ids[i];
    assert(e->name==names[id]&&e->desc==descriptions[id]);
    assert(e->name_len==(size_t)lang+1&&e->desc_len==(size_t)lang);
    assert(e->icon==id&&e->quantity==g_items[id]);
   }
  }
 }
 memset(g_items,0,sizeof(g_items));ui_inventory_snapshot(&cached);
 assert(cached.count[0]==0&&cached.count[1]==0);
 return 0;
}
'''
with tempfile.TemporaryDirectory() as t:
 p=Path(t);(p/'test.c').write_text(source)
 subprocess.run(['cc','-std=c99','-Wall','-Wextra','-Werror','-fsanitize=undefined',str(p/'test.c'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
print('PASS: cached inventory matches previous collector in four languages, empty and invalid entries')
