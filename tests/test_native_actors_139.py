"""Verify native actor pixels and unchanged story scripts across supported maps."""
from pathlib import Path
import json, struct, sys, subprocess, tempfile
from PIL import Image

r = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(r / 'tools'))
import prepare_world_v060 as w
game = r.parent / 'original'
key = bytes.fromhex(w.read_json(game / 'data/System.json')['encryptionKey'])
texts = w.read_json(game / 'data/I18NTexts.json')
w.PICTURE_IDS = w.read_json(r / 'assets/picture_v050_manifest.json')
audio = w.read_json(r / 'assets/audio_exact_v079.json')
w.EXACT_SE_IDS = {w.audio_key(x): x['id'] for x in audio if x['kind'] == 'se'}
w.EXACT_BGM_IDS = {w.audio_key(x): x['id'] for x in audio if x['kind'] == 'bgm'}
count = pages = 0
cache = {}
for mid in list(range(1,69))+[70]:
    data = w.adapt_stage_142(w.read_json(game / 'data' / f'Map{mid:03}.json'),mid)
    if not any(any(n in p['image']['characterName'] for n in ('エンリ', 'S-003', '吊'))
               for e in data['events'] if e for p in e['pages']):
        continue
    if mid == 9: data = w.adapt_plant1_worm(data)
    eb = (r / 'assets' / f'map{mid:03}_events.bin').read_bytes()
    _, width, height, transfers, sprites, _ = struct.unpack_from('<4s5H', eb)
    sb = 14 + width * height * 5 + transfers * 20
    vb = (r / 'assets' / f'map{mid:03}_vm.bin').read_bytes()
    _, ne, np, blob, _, _ = struct.unpack_from('<4sHHIII', vb)
    pb = 20 + ne * 10
    atlases = {}
    for i in range(ne):
        eid, x, y, first, number, _ = struct.unpack_from('<HHHHBB', vb, 20 + i * 10)
        for j, page in enumerate(data['events'][eid]['pages']):
            pg = struct.unpack_from('<BBBBHHBBHII', vb, pb + (first+j)*20)
            ref, off, size = pg[8:]
            assert vb[blob+off:blob+off+size] == (w.compile_vm_commands(page, texts,preserve_message_background=mid in (62,67,68)) if pg[7] else bytes([0])), (mid,eid,j)
            pages += 1
            if not ref:
                continue
            rec = struct.unpack_from('<6H2BH', eb, sb+(ref-1)*16)
            sx, sy, sw, sh, priority, flags, event_id = rec[2:]
            atlas_id, sx = sx >> 12, sx & 4095
            assert atlas_id < 2
            if atlas_id not in atlases:
                path = r / 'assets' / f'map{mid:03}_event_atlas{atlas_id or ""}.rgba8888'
                atlases[atlas_id] = Image.frombytes('RGBA', (512,512), path.read_bytes())
            name = page['image']['characterName']
            if not any(n in name for n in ('エンリ', 'S-003', '吊')) and not (mid in (67,68) and name=='蜘蛛'):
                continue
            assert flags & 4
            if name not in cache:
                cache[name] = w.load_encrypted_png(w.resolve_named_file(game/'img/characters', name), key)
            image = page['image']
            dirs = (2,4,6,8) if flags & 64 else [image['direction']]
            pats = range(3) if flags & (2|128) else [image['pattern']]
            for row, direction in enumerate(dirs):
                for slot, pattern in enumerate(pats):
                    original = w.extract_character_frame(cache[name], name, image['characterIndex'], direction, pattern)
                    assert original.size == (sw, sh), (mid, eid, name, original.size, (sw,sh))
                    expected = Image.new('RGBA', original.size)
                    expected.alpha_composite(original)
                    dx, dy = slot*sw, 0
                    if flags & 64:
                        if flags & 128:
                            dx += (row & 1)*3*sw
                            dy = (row >> 1)*sh
                        elif mid == 43 or 48 <= mid <= 70:
                            dx += (row & 1)*sw
                            dy = (row >> 1)*sh
                        else:
                            dy = row*sh
                    assert sx+dx+sw <= 512 and sy+dy+sh <= 512
                    actual = atlases[atlas_id].crop((sx+dx,sy+dy,sx+dx+sw,sy+dy+sh))
                    assert actual.tobytes() == expected.tobytes(), (mid,eid,name,direction,pattern)
                    count += 1

# The stair ceiling is foreground; tile identities and passage masks survive.
for mid in (38,41):
    data = w.read_json(game/'data'/f'Map{mid:03}.json')
    mb = (r/'assets'/f'map{mid:03}.bin').read_bytes()
    width, height = data['width'], data['height']
    tileset = w.read_json(game/'data/Tilesets.json')[data['tilesetId']]
    slots = {t:i+1 for i,t in enumerate(sorted(set(data['data'][:width*height*4])-{0}))}
    for i,tile in enumerate(data['data'][:width*height*4]):
        word = struct.unpack_from('<H', mb, 20+i*2)[0]
        assert word & 0x3fff == slots.get(tile,0)
        if 5888 <= tile < 5936:
            assert word & 0x8000
    for y in range(height):
        for x in range(width):
            assert mb[20+width*height*8+y*width+x] == w.build_pass_mask(data,tileset['flags'],x,y)

# Verify the original button page begins with BGM fade, then a 120-frame wait.
b = (r/'assets/map036_vm.bin').read_bytes()
_, ne, np, blob, _, _ = struct.unpack_from('<4sHHIII', b)
for i in range(ne):
    eid, x, y, first, number, _ = struct.unpack_from('<HHHHBB', b,20+i*10)
    if eid == 17:
        off, length = struct.unpack_from('<II',b,20+ne*10+(first+1)*20+12)
        assert b[blob+off:blob+off+6] == bytes([12,2,0,4,120,0])

# Run the actual reveal function and actual first-wait override in host C.
s = (r/'main.c').read_text()
helper = s[s.index('static unsigned int g_ambush_reveal_start;'):s.index('static void draw_event_sprite_record(')]
start = s.index('            /* Button-room arrival:')
override = s[start:s.index('            vm_wait_frames(frames,', start)]
code = '#include <assert.h>\n'+helper+'''\nint main(void) {
assert(ambush_reveal_opacity(33,46,0)==255);
int prev=0;
for(unsigned int i=0;i<7;i++){int a=ambush_reveal_opacity(34,51,100+i);assert(a>prev);prev=a;}
assert(prev==255 && ambush_reveal_opacity(34,51,120)==255);
g_ambush_reveal_started=0;assert(ambush_reveal_opacity(34,51,900)<255);
int source_map_id=36,source_event_id=17,frames=120;char buffer[10],*base=buffer,*p=buffer+6;
'''+override+'''
assert(frames==118);
frames=120;p=buffer+9;
'''+override+'''
assert(frames==120);
frames=120;p=buffer+6;source_map_id=35;
'''+override+'''
assert(frames==120);return 0;}
'''
with tempfile.TemporaryDirectory() as d:
    p = Path(d)
    (p/'test.c').write_text(code)
    subprocess.run(['cc','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True)
    subprocess.run([str(p/'test')],check=True)
print(f'PASS: {count} native actor frames, {pages} exact original script pages, stair depth/collisions, 2-frame timing and 6-frame reveal')
