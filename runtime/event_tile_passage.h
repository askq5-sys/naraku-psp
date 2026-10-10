/* MZ checks below-character tile events before the map layers. A star
 * tile has no passage effect; non-star tiles decide all four directions.
 * VM flag2 enables this metadata only in resources rebuilt with tile flags. */
static uint8_t event_tile_pass_mask(const MapState *m,int x,int y,uint8_t fallback)
{
    int i;
    for(i=0;i<m->vm_event_count;++i) {
        VmEventRecord ev;VmPageRecord pg;int cx,cy,active;
        if(!vm_read_event(m,i,&ev))continue;
        vm_event_contact_cell(m,&ev,&cx,&cy);
        if(cx!=x || cy!=y || !vm_active_page_index(m,&ev,&pg,&active))continue;
        if(!(pg.cond_flags&8) || (pg.flags&1))continue;
        if(ev.event_id>0 && ev.event_id<MAX_EVENT_ID &&
           g_event_active_page[ev.event_id]==active && g_event_through[ev.event_id])continue;
        return (uint8_t)(~(pg.cond_flags>>4)&15);
    }
    return fallback;
}

