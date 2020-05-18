"""This module defines a function to decompress render results in a directory"""

import os

from zipfile import ZipFile
from src.config.enums import RenderStatus
from src.utils.open_image import open_image


def get_extract_path(zfilepath):
    """Returns path in which results will be unzipped"""
    extract_path = os.path.splitext(zfilepath)[0]

    # If file/directory of this name already exists, append _number to name
    if os.path.exists(extract_path):
        i = 1
        while os.path.exists(f'{extract_path}_{str(i)}'):
            i = i + 1
        extract_path = f'{extract_path}_{str(i)}'

    return extract_path


def decompress_rendering_results(zfilepath, extract_path):
    """Decompresses rendering results in a directory named after the rendering name"""

    with ZipFile(zfilepath) as zfile:
        zfile.extractall(path=extract_path)
    os.remove(zfilepath)
