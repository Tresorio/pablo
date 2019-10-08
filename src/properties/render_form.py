import bpy
import math
from src.config.langs import TRADUCTOR, CONFIG_LANG


def update_max_cost(prop, ctx):
    del prop
    render_form = ctx.window_manager.tresorio_render_form
    user_credits = ctx.window_manager.tresorio_user_props.total_credits
    if render_form.timeout == 0 and render_form.price_per_hour > 0.0:
        render_form.max_timeout = math.floor(
            user_credits / render_form.price_per_hour)
        render_form.max_cost = render_form.max_timeout * render_form.price_per_hour
    else:
        render_form.max_timeout = render_form.timeout
        render_form.max_cost = render_form.price_per_hour * render_form.timeout


class TresorioRenderFormProps(bpy.types.PropertyGroup):

    default = TRADUCTOR['field']['default_render_name'][CONFIG_LANG]
    desc = TRADUCTOR['desc']['rendering_name'][CONFIG_LANG]
    rendering_name: bpy.props.StringProperty(
        description=desc,
        name='',
        maxlen=255,
        options={'HIDDEN', 'SKIP_SAVE'},
        default=default,
    )

    # TODO dynamic way of getting these infos (on gandalf)
    desc = TRADUCTOR['desc']['render_engines_list'][CONFIG_LANG]
    render_engines_list: bpy.props.EnumProperty(
        description=desc,
        name='',
        items=(
            ('CYCLES', 'Cycles', '', 'EMPTY_AXIS', 1),
            # ('EEVEE', 'Eevee', ''), # TODO fix hardware specific problem (X11, OpenGL) ...
        ),
        default='CYCLES',
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    # TODO dynamic way of getting these infos (on gandalf)
    desc = TRADUCTOR['desc']['output_formats_list'][CONFIG_LANG]
    output_formats_list: bpy.props.EnumProperty(
        description=desc,
        name='',
        items=(
            ('PNG', 'PNG', '', 'FILE_IMAGE', 1),
            ('JPEG', 'JPEG', '', 'FILE_IMAGE', 1),
            ('BMP', 'BMP', '', 'FILE_IMAGE', 1),
            ('AVIRAW', 'Avi_Raw', '', 'FILE_IMAGE', 1),
            ('AVIJPEG', 'Avi_JPEG', '', 'FILE_IMAGE', 1),
            ('IRIS', 'Iris', '', 'FILE_IMAGE', 1),
            ('IRIZ', 'Iriz', '', 'FILE_IMAGE', 1),
            ('JP2', 'JPEG_2000', '', 'FILE_IMAGE', 1),
            ('TGA', 'Targa', '', 'FILE_IMAGE', 1),
            ('RAWTGA', 'Targa_Raw', '', 'FILE_IMAGE', 1),
            ('HDR', 'HDR', '', 'FILE_IMAGE', 1),
            ('TIFF', 'TIFF', '', 'FILE_IMAGE', 1),
            ('CINEON', 'Cineon', '', 'FILE_IMAGE', 1),
            ('OPEN_EXR', 'OpenEXR', '', 'FILE_IMAGE', 1),
            ('OPEN_EXR_MULTILAYER', 'OpenEXR Multilayer', '', 'FILE_IMAGE', 1),
            ('DPX', 'DPX', '', 'FILE_IMAGE', 1),
            ('DDS', 'DDS', '', 'FILE_IMAGE', 1),
            ('JP2', 'JP2', '', 'FILE_IMAGE', 1),
        ),
        default='PNG',
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    render_pack: bpy.props.StringProperty(
        description='',
        name='',
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    desc = TRADUCTOR['desc']['render_types'][CONFIG_LANG]
    desc_frame = TRADUCTOR['desc']['render_type_frame'][CONFIG_LANG]
    desc_animation = TRADUCTOR['desc']['render_type_animation'][CONFIG_LANG]
    render_types: bpy.props.EnumProperty(
        description=desc,
        name='',
        items=(
            ('FRAME', 'Frame', desc_frame, 'RESTRICT_RENDER_OFF', 0),
            ('ANIMATION', 'Animation', desc_animation, 'RENDER_ANIMATION', 1),
        ),
        default='FRAME',
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    desc = TRADUCTOR['desc']['pack_textures'][CONFIG_LANG]
    pack_textures: bpy.props.BoolProperty(
        default=True,
        description=desc,
        name='',
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    desc = TRADUCTOR['desc']['timeout'][CONFIG_LANG]
    timeout: bpy.props.IntProperty(
        min=0,
        max=100_000,
        description=desc,
        name='',
        default=12,
        subtype='TIME',
        options={'HIDDEN', 'SKIP_SAVE'},
        update=update_max_cost,
    )

    upload_percent: bpy.props.FloatProperty(
        min=0,
        max=100,
        name='',
        description='',
        default=0,
        subtype='PERCENTAGE',
        options={'HIDDEN', 'SKIP_SAVE'},
        update=lambda a, b: None,
    )

    max_cost: bpy.props.FloatProperty(options={'HIDDEN', 'SKIP_SAVE'},)
    max_timeout: bpy.props.IntProperty(options={'HIDDEN', 'SKIP_SAVE'},)
    current_pack_index: bpy.props.IntProperty(options={'HIDDEN', 'SKIP_SAVE'},)
    price_per_hour: bpy.props.FloatProperty(options={'HIDDEN', 'SKIP_SAVE'},)

    @classmethod
    def register(cls):
        """Link to window manager so these settings are reset at launch"""
        bpy.types.WindowManager.tresorio_render_form = bpy.props.PointerProperty(
            type=cls,
            name='tresorio_render_form',
            options={'HIDDEN', 'SKIP_SAVE'}
        )

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.tresorio_render_form
