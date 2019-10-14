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
    upload_failed: bpy.props.BoolProperty(
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

    downloading_render_results: bpy.props.BoolProperty(
        name='',
        description='',
        options={'HIDDEN', 'SKIP_SAVE'},
        update=lambda a, b: None,
    )

    success_render_download: bpy.props.BoolProperty(
        name='',
        description='',
        options={'HIDDEN', 'SKIP_SAVE'},
        update=lambda a, b: None,
    )

    packing_textures: bpy.props.BoolProperty(
        name='',
        description='',
        options={'HIDDEN', 'SKIP_SAVE'},
        update=lambda a, b: None,
    )

    unpacking_textures: bpy.props.BoolProperty(
        name='',
        description='',
        options={'HIDDEN', 'SKIP_SAVE'},
        update=lambda a, b: None,
    )

    # TODO not enough credit on 403 on req_create_render

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
        del bpy.types.WindowManager.tresorio_report_props
