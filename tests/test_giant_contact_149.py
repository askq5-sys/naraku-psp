"""Compile the actual main-loop contact calls; verify logical-cell semantics."""
from pathlib import Path
import subprocess,tempfile
r=Path(__file__).resolve().parents[1];s=(r/'main.c').read_text()
a=s.index('            int logical_contact = map.id==72 && moving;')
b=s.index('            if (contact) {',a)
body=s[a:b]
pre=r'''#include <assert.h>
#include <stdio.h>
typedef struct {int id;} Map;
static int enemy_x,enemy_y,calls;
static int vm_run_event_at(Map*m,int x,int y,int trigger,void*atlas,int lang,int*px,int*py,int*dir){calls++;return x==enemy_x&&y==enemy_y;}
static int check(int mid,int moving,int tile_x,int tile_y,int target_x,int target_y){Map map={mid};void*char_atlas=0;int lang=0,direction_row=0;
'''
post=r'''return contact;}
int main(void){
/* Leaving a threatened cell horizontally, then turning down at the exit. */
enemy_x=14;enemy_y=5;calls=0;assert(!check(72,1,14,5,13,5)&&calls==1);
enemy_x=13;calls=0;assert(!check(72,1,13,5,13,6)&&calls==1);
/* Incoming/idle contact is still lethal; other chases retain both checks. */
assert(check(72,1,14,5,13,5));assert(check(72,0,13,5,13,6));
assert(check(68,1,13,5,13,6));
puts("PASS: actual main-loop collision calls use the committed destination on Map072, including the exit turn; incoming/idle and other chase contact preserved");}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'t.c';e=Path(td)/'t';p.write_text(pre+body+post)
 subprocess.run(['cc','-std=c99',str(p),'-o',str(e)],check=True)
 subprocess.run([str(e)],check=True)
