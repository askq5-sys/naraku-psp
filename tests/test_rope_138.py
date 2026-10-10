from pathlib import Path
import subprocess,tempfile
r=Path(__file__).resolve().parents[1]
s=(r/'main.c').read_text()
assert s.count('reconcile_consumed_items();')==3
code='#include <stdint.h>\n#include <assert.h>\nstatic uint8_t g_switches[1601];\nstatic int16_t g_items[128];\n'+(r/'runtime/consumed_items.h').read_text()+'\nint main(void){\ng_items[48]=1;g_switches[320]=1;reconcile_consumed_items();assert(g_items[48]==1);\ng_switches[350]=1;reconcile_consumed_items();assert(g_items[48]==1);\ng_switches[351]=1;g_items[55]=1;reconcile_consumed_items();assert(g_items[48]==0&&g_items[55]==1);\ng_items[48]=3;reconcile_consumed_items();assert(g_items[48]==0);\nreconcile_consumed_items();assert(g_items[48]==0);\ng_switches[351]=0;g_items[48]=1;reconcile_consumed_items();assert(g_items[48]==1);\nreturn 0;}\n'
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(code)
 subprocess.run(['cc','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
print('PASS: early door unlock, descent completion, stale duplicate counts, unrelated items, idempotence and new game')
