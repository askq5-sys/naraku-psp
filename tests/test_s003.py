from pathlib import Path
import json,re,struct
r=Path(__file__).resolve().parents[1]
for mid,page in [(24,5),(25,1)]:
 original=json.load(open(r.parent/f'original/data/Map{mid:03d}.json'))['events'][3]['pages'][page]['moveRoute']['list']
 expected=b''.join(struct.pack('<Bhh',c['code'],(c.get('parameters')or[0])[0],0)for c in original if c['code'])
 h=(r/'runtime/s003_routes.h').read_text();got=bytes(map(int,re.search(r's003_route_'+str(mid)+r'\[\] = \{([^}]+)',h)[1].split(',')));assert got==expected
 raw=(r/'assets'/f'map{mid:03d}_events.bin').read_bytes();_,w,h,nt,ns,_=struct.unpack_from('<4s5H',raw);base=14+w*h*5+nt*struct.calcsize("<HHHBBHBBHBBHBB")
 records=[struct.unpack_from('<HHHHHHBBH',raw,base+i*16)for i in range(ns)]
 walking=[x for x in records if x[-1]==3 and x[-2]&0x80];assert walking
 for x in walking:
  _,_,sx,sy,sw,sh,priority,flags,eid=x;assert flags&0x40 and sx+6*sw<=512 and sy+2*sh<=512 and flags&4
s=(r/'main.c').read_text();assert 'if (is_chase_map(map.id)'in s
print('PASS: original custom movement routes, three walking patterns/four directions, atlas bounds and stationary-player contact')
