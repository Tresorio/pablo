import bpy
from src.properties.render_form import update_max_cost
from src.config.langs import TRADUCTOR, CONFIG_LANG


def set_render_pack(pack, context):
    packs = context.window_manager.tresorio_render_packs
    is_there_any_pack = False
    for p in packs:
        if p.is_selected is True:
            is_there_any_pack = True
            break
    if is_there_any_pack is False:
        pack.is_selected = True
        return
    if pack.is_selected is False:
        return
    context.window_manager.tresorio_render_form.render_pack = pack.name
    context.window_manager.tresorio_render_form.price_per_hour = pack.cost
    update_max_cost(None, context)
    for any_pack in packs:
        if any_pack != pack:
            any_pack.is_selected = False


class TresorioRenderPacksProps(bpy.types.PropertyGroup):

    is_selected: bpy.props.BoolProperty(
        update=set_render_pack,
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

    description: bpy.props.StringProperty(
        options={'HIDDEN', 'SKIP_SAVE'},
        update=lambda a, b: None,
    )

    @classmethod
    def register(cls):
        """Link to window manager so these settings are reset at launch"""
        desc = TRADUCTOR['desc']['render_packs'][CONFIG_LANG]
        bpy.types.WindowManager.tresorio_render_packs = bpy.props.CollectionProperty(
            type=cls,
            name='tresorio_render_form',
            description=desc,
            options={'HIDDEN', 'SKIP_SAVE'},
        )

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.tresorio_render_packs
