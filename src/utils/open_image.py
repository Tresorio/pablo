import sys
import subprocess

IMG_VIEWER = {'win32': 'explorer',
              'linux': 'xdg-open',
              'darwin': 'open'}


def open_image(filepath):
    subprocess.run([IMG_VIEWER[sys.platform], filepath])
