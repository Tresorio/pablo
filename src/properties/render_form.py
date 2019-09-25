import bpy
from src.config.langs import TRADUCTOR, CONFIG_LANG


def update_max_cost(prop, ctx):
    del prop
    render_form = ctx.window_manager.tresorio_render_form
    user_credits = ctx.window_manager.tresorio_user_props.total_credits
    if render_form.timeout == 0:
        render_form.max_cost = render_form.price_per_hour * user_credits
    else:
        render_form.max_cost = render_form.price_per_hour * render_form.timeout


class TresorioRenderFormProps(bpy.types.PropertyGroup):

    default = TRADUCTOR['field']['default_render_name'][CONFIG_LANG]
    desc = TRADUCTOR['desc']['rendering_name'][CONFIG_LANG]
    rendering_name: bpy.props.StringProperty(
        description=desc,
        name='',
        maxlen=255,
        options={'SKIP_SAVE'},
        default=default,
    )

    # TODO dynamic way of getting these infos (on gandalf)
    desc = TRADUCTOR['desc']['render_engines_list'][CONFIG_LANG]
    render_engines_list: bpy.props.EnumProperty(
        description=desc,
        name='',
        items=(
            ('CYCLES', 'Cycles', ''),
            ('EEVEE', 'Eevee', ''),
        ),
        default='CYCLES'
    )

    # TODO dynamic way of getting these infos (on gandalf)
    desc = TRADUCTOR['desc']['output_formats_list'][CONFIG_LANG]
    output_formats_list: bpy.props.EnumProperty(
        description=desc,
        name='',
        items=(
            ('PNG', 'PNG', ''),
        ),
        default='PNG'
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
        default='FRAME'
    )

    desc = TRADUCTOR['desc']['timeout'][CONFIG_LANG]
    timeout: bpy.props.IntProperty(
        min=0,
        max=1024,
        description=desc,
        name='',
        default=12,
        subtype='TIME',
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

    max_cost: bpy.props.FloatProperty()
    current_pack_index: bpy.props.IntProperty()
    price_per_hour: bpy.props.FloatProperty()

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
