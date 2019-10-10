**TODO's:**

    On Pablo:
        - use threading for upload and download tasks (as they're heavier, it's not performant to use asyncio for this)
        - Count uptime in blender and not every 3 seconds
        - Figure out what happends if multiple addons use the asyncio module (and async_loop code)
        - Send the last line of logs to blender (so the user can see what happens) ?
        - Have an option to enable the plugin in every .blend of the user
        - Include Eevee (see if it is interesting)
        - Set the language according to blender
        - Alias bpy.data.wm['WinMan'] (at least try it)
        - IsInstance instead of type(cls)
        - error 403 -> httpstatus

    On Gandalf:
        - Fix credit debit (way more than expected atm)
        - Add a way to loadBalance using single frame separation

    On Paulette:
        - Add a way to upload renders as they appear
        - Add a way to merge multiple frame fragments into one

**Legals:**

    - Credit the authors of the icons (actually get our own icons would be better)