**TODO's:**

    On Pablo:
        - Check if blender loads the first scene or the last opened
        - Add a way to reuse a .blend for another render, just tweaking the settings
        - Fix crash when big number of frames -> DO NOT DO ONE REQUEST PER FRAME
        - Fix tile size problem on gpus (sometimes it gives tiles to cpus and it slows down the render)
        - Refresh only the task targeted and not all
        - Get gpu and cpu models in the json so the user has more information
        - Button to updgrade the addon to the newest version
        - Let user specify default output directory -> `Download when over` option
        - Count uptime on front
        - Create a tutorial on first launch
        - Feedback panel of the user to get his advice
        - Bind key `Enter` to `login` in the Connection panel
        - Send the last line of logs to blender (so the user can see what happens) ?
        - Figure out what happens if multiple addons use the asyncio module (and async_loop code)

    On Pablo with next blender:
        - On hover description of render pack -> (ops with future dynamic description)

    On Gandalf:
        - Email on render end
        - Fix crash when big number of frames
        - Packs: GPU only - CPU only - CPU+GPU
        - Fix credit debit (recredits more than expected sometimes)
        - Add a way to loadBalance using single frame separation

    On Paulette:
        - Versionning for big file changes instead of reuploading every time
        - Check if the use of -s -e -a instead of many -f is faster
        - Maybe blender's stdout slows down the render as there are MANY lines output
        - Store the render results as HDR (for example) so we can convert to any other file format later
        - Add a way to upload renders as they appear
        - Add a way to merge multiple frame fragments into one
