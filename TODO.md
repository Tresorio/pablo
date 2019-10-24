**TODO's:**

    On Pablo:
        - `Download all` operator
        - Better UI for expand of settings and render pack
        - Test the plugin
        - Nas JWT handling
        - Add some keybinds for a better UX
        - Let user specify default output directory -> `Download when over` option
        - Count uptime on front
        - Create a tutorial on first launch
        - Feedback panel of the user to get his advice
        - Button to updgrade the addon to the newest version
        - Figure out what happens if multiple addons use the asyncio module (and async_loop code)

    On Pablo with next blender:
        - On hover description of render pack -> (ops with future dynamic description)

    On Gandalf:
        - Packs: GPU only - CPU only - CPU+GPU
        - Pass param auto_tile_size to Paulette (given by pablo)
        - Pass param [HYBRID | GPU | CPU] to paulette
        - Add a way to loadBalance using single frame separation
        - Email on render end

    On Paulette:
        - Why some cpus are slower than others
        - Versionning for big file changes instead of reuploading every time
        - Check if the use of -s -e -a instead of many -f is faster
        - Maybe blender's stdout slows down the render as there are MANY lines output
        - Store the render results as HDR (for example) so we can convert to any other file format later
        - Add a way to upload renders as they appear / Count the number of artifacts
        - Add a way to merge multiple frame fragments into one
