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


def decompress_rendering_results(zfilepath, open_on_download, render_details):
    """Decompresses rendering results in a directory named after the rendering name"""

    with ZipFile(zfilepath) as zfile:
        extract_path = get_extract_path(zfilepath)
        zfile.extractall(path=extract_path)
        if open_on_download:
            # Open the artifacts directory if there is no error, else base directory
            if render_details['status'] != RenderStatus.ERROR:
                image = zfile.namelist()[0].rstrip('/')
            else:
                image = ""
            image_path = os.path.join(extract_path, image)
            open_image(image_path)
    os.remove(zfilepath)
