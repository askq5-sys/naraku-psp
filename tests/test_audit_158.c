#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../runtime/laser_chase_trail.h"
#include "../runtime/render_boundaries.h"
#include "laser_trail_reference.inc"
int main(void) {
 laser_chase_reset();reference_chase_reset();
 int x=0,y=0;
 for(int i=0;i<20000;++i) {
  if(i%317==0){laser_chase_reset();reference_chase_reset();}
  int d=rand()%4;x+=(d==0)-(d==1);y+=(d==2)-(d==3);
  if(i%401==0){x+=10;y+=10;}
  laser_chase_record(x,y);reference_chase_record(x,y);
  assert(laser_chase_trail.count==reference_chase_trail.count);
  for(int j=0;j<laser_chase_trail.count;++j){
   int k=(laser_chase_trail.head+j)&255;
   assert(laser_chase_trail.x[k]==reference_chase_trail.x[j]);
   assert(laser_chase_trail.y[k]==reference_chase_trail.y[j]);
  }
  int ex=x+(rand()%5)-2,ey=y+(rand()%5)-2;
  assert(laser_chase_step(ex,ey)==reference_chase_step(ex,ey));
 }
 for(int mid=1;mid<=139;++mid)for(int xi=0;xi<17;++xi)for(int yi=0;yi<25;++yi){
  float wx=(xi+.5f)*24,wy=(yi+1.f)*24;
  int active=mid==105 && wx>=1.5f*24 && wx<=3.5f*24 && wy<=20.f*24;
  for(int cam=-20;cam<900;cam+=13){
   int expected=active?(int)floorf(7.3f+16.f*24-cam):-1;
   if(active){if(expected<0)expected=0;if(expected>272)expected=272;}
   assert(secret_ladder_clip_top(mid,wx,wy,24,7.3f,cam,272)==expected);
  }
 }
 puts("PASS: 20000 trail operations preserve chase behavior; ladder scope and camera clipping unchanged");
}
