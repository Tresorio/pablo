"""This module defines the properties of a render"""

from src.config.langs import TRADUCTOR, CONFIG_LANG
import bpy


class TresorioRendersDetailsProps(bpy.types.PropertyGroup):
    """Details properties of a render"""
    id: bpy.props.StringProperty(update=lambda a, b: None,
                                 options={'HIDDEN', 'SKIP_SAVE'})

    # Render specifics
    project_name: bpy.props.StringProperty(
        update=lambda a, b: None, options={'HIDDEN', 'SKIP_SAVE'})
    name: bpy.props.StringProperty(
        update=lambda a, b: None, options={'HIDDEN', 'SKIP_SAVE'})
    gpu: bpy.props.IntProperty(
        update=lambda a, b: None, options={'HIDDEN', 'SKIP_SAVE'})
    cpu: bpy.props.IntProperty(
        update=lambda a, b: None, options={'HIDDEN', 'SKIP_SAVE'})
    ram: bpy.props.IntProperty(
        update=lambda a, b: None, options={'HIDDEN', 'SKIP_SAVE'})
    cost: bpy.props.FloatProperty(
        update=lambda a, b: None, options={'HIDDEN', 'SKIP_SAVE'})
    total_cost: bpy.props.FloatProperty(
        update=lambda a, b: None, options={'HIDDEN', 'SKIP_SAVE'})
    engine: bpy.props.StringProperty(
        update=lambda a, b: None, options={'HIDDEN', 'SKIP_SAVE'})
    type: bpy.props.StringProperty(
        update=lambda a, b: None, options={'HIDDEN', 'SKIP_SAVE'})
    output_format: bpy.props.StringProperty(
        update=lambda a, b: None, options={'HIDDEN', 'SKIP_SAVE'})
    launched: bpy.props.BoolProperty(
        update=lambda a, b: None, options={'HIDDEN', 'SKIP_SAVE'})
    mode: bpy.props.StringProperty(
        update=lambda a, b: None, options={'HIDDEN', 'SKIP_SAVE'})

    # Advancement
    number_of_fragments: bpy.props.IntProperty(
        update=lambda a, b: None, options={'HIDDEN', 'SKIP_SAVE'})
    total_frames: bpy.props.IntProperty(
        update=lambda a, b: None, options={'HIDDEN', 'SKIP_SAVE'})
    rendered_frames: bpy.props.IntProperty(
        update=lambda a, b: None, options={'HIDDEN', 'SKIP_SAVE'})
    uptime: bpy.props.IntProperty(
        update=lambda a, b: None, options={'HIDDEN', 'SKIP_SAVE'})
    status: bpy.props.StringProperty(
        update=lambda a, b: None, options={'HIDDEN', 'SKIP_SAVE'})
    downloading: bpy.props.BoolProperty(
        update=lambda a, b: None, default=False, options={'HIDDEN', 'SKIP_SAVE'})

    desc = TRADUCTOR['desc']['render_advancement_percent'][CONFIG_LANG]
    progression: bpy.props.FloatProperty(
        min=0,
        max=100,
        name='',
        description=desc,
        default=0,
        subtype='PERCENTAGE',
        options={'HIDDEN', 'SKIP_SAVE'},
        update=lambda a, b: None,
    )

    @classmethod
    def register(cls):
        """Link to window manager so these settings are reset at launch"""
        desc = TRADUCTOR['desc']['render_details'][CONFIG_LANG]
        bpy.types.WindowManager.tresorio_renders_details = bpy.props.CollectionProperty(
            type=cls,
            name='tresorio_renders_details',
            description=desc,
            options={'HIDDEN', 'SKIP_SAVE'},
        )
        bpy.types.WindowManager.tresorio_renders_list_index = bpy.props.IntProperty(
            name='',
            description='',
            options={'HIDDEN', 'SKIP_SAVE'},
            update=lambda a, b: None,
        )

    @classmethod
    def unregister(cls):
        """Unregister the class from blender"""
        del bpy.types.WindowManager.tresorio_renders_details
