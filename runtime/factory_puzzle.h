/* The original timeout resets checkpoints 1–4 but leaves checkpoint 5 and
 * door progress armed. A failed sequence must restart from its first lever. */
static void reset_factory_checkpoint_tail(int map_id,int event_id,int trigger)
{
    if(map_id==49 && event_id==16 && trigger==3 && g_switches[460]) {
        memset(g_switches+541,0,12);
        /* 561/562 spawn the killer, 565 controls the entrance and 567 is
         * his scene pose. Only the door flags belong to puzzle progress. */
        g_switches[566]=g_switches[568]=g_switches[569]=g_switches[570]=0;
    }
}
