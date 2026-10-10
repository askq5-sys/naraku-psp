/* The next story arc swaps a single leader among these original actors.
 * PG60's spare high bits persist their membership without resizing saves. */
static uint8_t g_player_party_mask = 1;
static int player_form_bit(int actor)
{
    return actor==1 ? 1 : actor==4 ? 2 : actor==5 ? 4 : actor==6 ? 8 : actor==7 ? 16 : actor==8 ? 32 : actor==9 ? 64 : actor==10 ? 128 : 0;
}
static void player_change_party(int actor, int remove_actor)
{
    int bit=player_form_bit(actor);
    if(remove_actor) g_player_party_mask &= (uint8_t)~bit;
    else g_player_party_mask |= (uint8_t)bit;
}
static int player_actor_from_mask(uint8_t mask)
{
    return (mask&1) ? 1 : (mask&2) ? 4 :
           (mask&4) ? 5 : (mask&8) ? 6 : (mask&16) ? 7 : (mask&32) ? 8 : (mask&64) ? 9 : (mask&128) ? 10 : 1;
}
static int player_form_actor(void) { return player_actor_from_mask(g_player_party_mask); }
static uint8_t player_form_save_bits(void) { return (uint8_t)(g_player_party_mask<<2); }
static void player_form_restore_bits(uint8_t flags)
{
    g_player_party_mask=(flags>>2)&63;
    if(!g_player_party_mask) g_player_party_mask=1; /* Earlier PG60 saves. */
}
