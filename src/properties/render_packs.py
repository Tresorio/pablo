"""This module defines the render packs properties"""

from src.config.langs import TRADUCTOR, CONFIG_LANG
from src.properties.render_form import update_max_cost
import bpy


def get_selected_pack():
    """
        Returns the currently selected pack, None if there is no pack
    """
    packs = bpy.context.window_manager.tresorio_render_packs
    for pack in packs:
        if pack.is_selected:
            return pack
    return None


def set_render_pack(pack: 'TresorioRenderPacksProps',
                    context: bpy.types.Context
                    ) -> None:
    """Set the render pack to the selected one"""
    packs = context.window_manager.tresorio_render_packs
    is_there_any_pack = False
    for curr_pack in packs:
        if curr_pack.is_selected:
            is_there_any_pack = True
            break
    if not is_there_any_pack:
        pack.is_selected = True
        return
    if not pack.is_selected:
        return
    context.scene.tresorio_render_form.render_pack = pack.name
    context.scene.tresorio_render_form.price_per_hour = pack.cost
    context.scene.tresorio_render_form.last_renderpack_selected = pack.name
    update_max_cost(None, context)
    for any_pack in packs:
        if any_pack != pack:
            any_pack.is_selected = False


class TresorioRenderPacksProps(bpy.types.PropertyGroup):
    """Render pack properties"""
    desc = TRADUCTOR['desc']['render_packs'][CONFIG_LANG]
    is_selected: bpy.props.BoolProperty(
        update=set_render_pack,
        description=desc,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    name: bpy.props.StringProperty(
        update=lambda a, b: None,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    cost: bpy.props.FloatProperty(
        min=0,
        update=lambda a, b: None,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    gpu: bpy.props.IntProperty(
        min=0,
        update=lambda a, b: None,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    cpu: bpy.props.IntProperty(
        min=0,
        update=lambda a, b: None,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    ram: bpy.props.IntProperty(
        min=0,
        update=lambda a, b: None,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    description: bpy.props.StringProperty(
        update=lambda a, b: None,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    @classmethod
    def register(cls):
        """Link to window manager so these settings are reset at launch"""
        bpy.types.WindowManager.tresorio_render_packs = bpy.props.CollectionProperty(
            type=cls,
            name='tresorio_render_form',
            options={'HIDDEN', 'SKIP_SAVE'},
        )

    @classmethod
    def unregister(cls):
        """Unregister the class from blender"""
        del bpy.types.WindowManager.tresorio_render_packs
