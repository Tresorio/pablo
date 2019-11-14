"""This module defines image viewer utilities"""

import sys
import subprocess

IMG_VIEWER = {'win32': 'explorer',
              'linux': 'xdg-open',
              'darwin': 'open'}


def open_image(filepath: str) -> None:
    """Open an image using the system's default image viewer

    Arg:
        filepath: filepath of the image to open
    """
    subprocess.run([IMG_VIEWER[sys.platform], filepath])
