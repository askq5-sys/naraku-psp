#include <assert.h>
#include <string.h>
#include <stdlib.h>
#include "../runtime/laser_chase_trail.h"
int main(void) {
 laser_chase_reset();
 laser_chase_record(0,0);laser_chase_record(1,0);laser_chase_record(2,0);
 laser_chase_record(2,1);laser_chase_record(2,2);laser_chase_record(1,2);
 assert(laser_chase_step(0,0)==3); /* current player is left/down: no shortcut */
 assert(laser_chase_step(1,0)==3);
 assert(laser_chase_step(2,0)==1);
 assert(laser_chase_step(2,1)==1);
 assert(laser_chase_step(2,2)==2);
 assert(laser_chase_step(1,2)==0);
 laser_chase_record(0,2);assert(laser_chase_step(1,2)==2);
 laser_chase_record(20,20);assert(laser_chase_step(0,2)==-1);
 laser_chase_reset();
 for(int i=0;i<300;++i)laser_chase_record(i,0);
 assert(laser_chase_trail.count==256);
 assert(laser_chase_step(44,0)==3);
 laser_chase_reset();assert(laser_chase_step(44,0)==-1);
 return 0;
}
