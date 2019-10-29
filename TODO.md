**TODO's:**

    On Pablo:
        - Add a way to download logs of a render
        - Validate render delete
        - `Download all` operator
        - Test the plugin
        - Nas JWT handling
        - Add some keybinds for a better UX
        - Let user specify default output directory -> `Download when over` option
        - Create a tutorial on first launch
        - Feedback panel of the user to get his advice
        - Button to updgrade the addon to the newest version
        - Figure out what happens if multiple addons use the asyncio module (and async_loop code)

    On Pablo with next blender:
        - On hover description of render pack -> (ops with future dynamic description)

    On Gandalf:
        - Add a way to loadBalance using single frame separation
        - Email on render end

    On Paulette:
        - Add a final task to regroup logs (atm each task erases 'logs.txt' on nassim), frame fragments
        - Add a task for file conversion
        - Why some cpus are slower than others
        - Versionning for big file changes instead of reuploading every time
        - Check if the use of -s -e -a instead of many -f is faster
        - Maybe blender's stdout slows down the render as there are MANY lines output
        - Store the render results as HDR (for example) so we can convert to any other file format later
        - Add a way to upload renders as they appear / Count the number of artifacts
        - Add a way to merge multiple frame fragments into one
