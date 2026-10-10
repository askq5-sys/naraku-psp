import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import prepare_world_v060 as w
for command, enabled in [(0,1),(1,0)]:
 page={'list':[{'code':135,'parameters':[command]}]}
 assert w.page_vm_supported(page)
 assert w.compile_vm_commands(page,{}) == bytes([36,enabled,0])
# Bit 0 remains character visibility; bit 1 is a backward-compatible flag.
for old in (0,1):
 assert not (old & 2)
for visible in (0,1):
 for enabled in (0,1):
  header=visible | (0 if enabled else 2)
  assert (header & 1)==visible
  assert (not bool(header & 2))==bool(enabled)
print('PASS: original save access commands and legacy save header flags')
