import bpy
import sys
from src.ui.popup import popup, alert, notif
import pathlib
from blender_asset_tracer import pack, bpathlib


def print_error(e):
    print(e)
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print(exc_type, exc_tb.tb_frame.f_code.co_filename, exc_tb.tb_lineno)
    alert(str(e))


def pack_scene(tpath: str):

    bpy.ops.file.report_missing_files()

    bpath = pathlib.Path(bpy.data.filepath)
    print("Packing", bpath, "into", tpath)

    bpath = bpathlib.make_absolute(bpath)
    ppath = bpathlib.make_absolute(bpath).parent

    packer = pack.Packer(bpath, ppath, tpath)

    packer.strategise()
    for missing_file in packer.missing_files:
        notif('Warning - Missing file ' + str(missing_file))
    packer.execute()

