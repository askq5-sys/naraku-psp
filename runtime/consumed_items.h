/* Original Map044 event4 sets switch351 after the rope descent completes.
 * Earlier door unlocking (switch320) deliberately keeps the rope. Reconcile
 * legacy inventory counts without repeating the scene or changing its flags. */
static void reconcile_consumed_items(void)
{
    if (g_switches[351]) g_items[48] = 0;
}
