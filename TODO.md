**TODO's:**

    On Pablo:
        - Have an option to enable the plugin in every .blend of the user
        - Figure out what happends if multiple addons use the asyncio module (and async_loop code)
        - Automatic refresh of UI (user information, renderpacks and user's renders)
        - Include Eevee (see if it is interesting)
        - use threading for upload and download tasks (as they're heavier, it's not performant to use asyncio for this)
        - Add a way for the user to select a pack and the number of farmers (farmers * pack)
        - Send the last line of logs to blender (so the user can see what happens) ?

    On Gandalf:
        - Farms are now minimal fragments -> add a param `number of fragments`
        - Fix credit debit (way more than expected atm)
        - Add a way to loadBalance using single frame separation

    On Paulette:
        - Vcpus are not allocated correctly, atm we allocate full cpus
        - Add a way to upload renders as they appear
        - Add a way to merge multiple frame fragments into one

**Legals:**

    - Credit the authors of the icons (actually get our own icons would be better)