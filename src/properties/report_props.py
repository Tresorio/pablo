"""This module defines the properties reporting the status of the addon"""

import bpy


class TresorioReportProps(bpy.types.PropertyGroup):
    """These settings are used to display error message on the addon"""

    # Login
    login_in: bpy.props.BoolProperty(
        name='',
        description='',
        default=False,
        options={'HIDDEN', 'SKIP_SAVE'},
        update=lambda a, b: None,
    )

    # Uploading
    uploading_blend_file: bpy.props.BoolProperty(
        default=False,
        name='',
        description='',
        options={'HIDDEN', 'SKIP_SAVE'},
        update=lambda a, b: None,
    )

    # Fetching user info
    fetching_user_info: bpy.props.BoolProperty(
        default=False,
        name='',
        description='',
        options={'HIDDEN', 'SKIP_SAVE'},
        update=lambda a, b: None,
    )
    fetch_user_info_failed: bpy.props.BoolProperty(
        default=False,
        name='',
        description='',
        options={'HIDDEN', 'SKIP_SAVE'},
        update=lambda a, b: None,
    )

    packing_textures: bpy.props.BoolProperty(
        name='',
        default=False,
        description='',
        options={'HIDDEN', 'SKIP_SAVE'},
        update=lambda a, b: None,
    )

    unpacking_textures: bpy.props.BoolProperty(
        name='',
        default=False,
        description='',
        options={'HIDDEN', 'SKIP_SAVE'},
        update=lambda a, b: None,
    )

    creating_render: bpy.props.BoolProperty(
        name='',
        default=False,
        description='',
        options={'HIDDEN', 'SKIP_SAVE'},
        update=lambda a, b: None,
    )

    deleting_all_renders: bpy.props.BoolProperty(
        name='',
        default=False,
        description='',
        options={'HIDDEN', 'SKIP_SAVE'},
        update=lambda a, b: None,
    )

    @classmethod
    def register(cls):
        """Link to window manager so these settings are reset at launch"""
        bpy.types.WindowManager.tresorio_report_props = bpy.props.PointerProperty(
            type=cls,
            name='tresorio_report_props',
            options={'HIDDEN', 'SKIP_SAVE'}
        )

    @classmethod
    def unregister(cls):
        """Unregister the class from blender"""
        del bpy.types.WindowManager.tresorio_report_props
