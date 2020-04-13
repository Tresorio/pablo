"""This module defines the properties for the render form"""

import math

from src.config.enums import RenderTypes
from src.config.langs import TRADUCTOR, CONFIG_LANG
import bpy


def set_frame_type(prop: 'TresorioRenderFormProps',
                   value: bool
                   ) -> None:
    """Set the frame type to the right value"""
    del value
    if not prop.is_switching_render_type:
        prop['nb_farmers'] = 1
        prop.is_switching_render_type = True
        prop.is_animation_selected = False
        prop.is_frame_selected = True
        prop.is_switching_render_type = False


def set_animation_type(prop: 'TresorioRenderFormProps',
                       value: bool
                       ) -> None:
    """Set the animation type to the right value"""
    del value
    if not prop.is_switching_render_type:
        prop.is_switching_render_type = True
        prop.is_frame_selected = False
        prop.is_animation_selected = True
        prop.is_switching_render_type = False


def get_render_type() -> str:
    """Return the type of the render"""
    render_form = bpy.context.scene.tresorio_render_form
    if render_form.is_frame_selected:
        return RenderTypes.FRAME
    return RenderTypes.ANIMATION

class TresorioRenderFormProps(bpy.types.PropertyGroup):
    """Render form panel"""
    desc = TRADUCTOR['desc']['show_settings'][CONFIG_LANG]
    show_settings: bpy.props.BoolProperty(
        name='',
        default=True,
        description=desc,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    desc = TRADUCTOR['desc']['rendering_name'][CONFIG_LANG]
    rendering_name: bpy.props.StringProperty(
        description=desc,
        name='',
        default=TRADUCTOR['field']['default_render_name'][CONFIG_LANG],
        maxlen=255,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    number_of_frames: bpy.props.IntProperty(
        update=lambda a,b: None, options={'HIDDEN', 'SKIP_SAVE'}, default=-1
    )

    desc = TRADUCTOR['desc']['render_engines_list'][CONFIG_LANG]
    render_engines_list: bpy.props.EnumProperty(
        description=desc,
        name='',
        items=(
            ('CYCLES', 'Cycles', '', 'EMPTY_AXIS', 1),
            ('EEVEE', 'Eevee (experimental !)', '', 'EMPTY_AXIS', 2)
        ),
        default='CYCLES',
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    desc = TRADUCTOR['desc']['output_formats_list'][CONFIG_LANG]
    output_formats_list: bpy.props.EnumProperty(
        description=desc,
        name='',
        items=(
            ('PNG', 'PNG', ''),
            ('JPEG', 'JPEG', ''),
            ('BMP', 'BMP', ''),
            ('IRIS', 'Iris', ''),
            ('IRIZ', 'Iriz', ''),
            ('JP2', 'JPEG_2000', ''),
            ('TGA', 'Targa', ''),
            ('RAWTGA', 'Targa_Raw', ''),
            ('HDR', 'HDR', ''),
            ('TIFF', 'TIFF', ''),
            ('CINEON', 'Cineon', ''),
            ('OPEN_EXR', 'OpenEXR', ''),
            ('OPEN_EXR_MULTILAYER', 'OpenEXR Multilayer', ''),
            ('DPX', 'DPX', ''),
            ('DDS', 'DDS', ''),
            ('JP2', 'JP2', ''),
        ),
        default='PNG',
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    is_switching_render_type: bpy.props.BoolProperty(
        description='',
        name='',
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    desc = TRADUCTOR['desc']['render_type_frame'][CONFIG_LANG]
    is_frame_selected: bpy.props.BoolProperty(
        description=desc,
        default=True,
        name='',
        options={'HIDDEN', 'SKIP_SAVE'},
        update=set_frame_type,
    )

    desc = TRADUCTOR['desc']['render_type_animation'][CONFIG_LANG]
    is_animation_selected: bpy.props.BoolProperty(
        description=desc,
        default=False,
        name='',
        options={'HIDDEN', 'SKIP_SAVE'},
        update=set_animation_type,
    )

    desc = TRADUCTOR['desc']['pack_textures'][CONFIG_LANG]
    pack_textures: bpy.props.BoolProperty(
        default=True,
        description=desc,
        name='',
        options={'HIDDEN', 'SKIP_SAVE'},
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

    desc = TRADUCTOR['desc']['auto_tile_size'][CONFIG_LANG]
    auto_tile_size: bpy.props.BoolProperty(
        description=desc,
        default=True,
        name='',
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    desc = TRADUCTOR['desc']['use_optix'][CONFIG_LANG]
    use_optix: bpy.props.BoolProperty(
        description=desc,
        default=True,
        name='',
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    project_id: bpy.props.StringProperty(
        description='',
        name='',
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    @classmethod
    def register(cls) -> None:
        """Link to Scene so these settings are kept in Scene"""
        bpy.types.Scene.tresorio_render_form = bpy.props.PointerProperty(
            type=cls,
            name='tresorio_render_form',
            options={'HIDDEN', 'SKIP_SAVE'}
        )

    @classmethod
    def unregister(cls) -> None:
        """Unregister the class from blender"""
        del bpy.types.Scene.tresorio_render_form
