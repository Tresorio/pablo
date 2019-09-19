import bpy
from src.utils.email import get_email_from_conf, set_email_in_conf, remove_email_from_conf
from src.utils.password import switch_password_visibility
from src.config.langs import set_new_lang, TRADUCTOR, CONFIG_LANG, ALL_LANGS


class TresorioUserProps(bpy.types.PropertyGroup):

    is_logged: bpy.props.BoolProperty(
        name='',
        options={'SKIP_SAVE'},
        default=False,
    )

    token: bpy.props.StringProperty(
        name='',
        options={'SKIP_SAVE'},
        default='',
    )

    langs: bpy.props.EnumProperty(
        name='',
        items=(ALL_LANGS['eng'], ALL_LANGS['fr']),
        update=set_new_lang,
        default=ALL_LANGS[CONFIG_LANG][0],
    )

    conf_email = get_email_from_conf()
    desc = TRADUCTOR['desc']['mail'][CONFIG_LANG]
    email: bpy.props.StringProperty(
        name='',
        description=desc,
        maxlen=128,
        options={'SKIP_SAVE'},
        default=conf_email,
    )

    desc = TRADUCTOR['desc']['password'][CONFIG_LANG]
    hidden_password: bpy.props.StringProperty(
        name='',
        description=desc,
        maxlen=128,
        default='',
        options={'SKIP_SAVE'},
        subtype='PASSWORD',
    )

    desc = TRADUCTOR['desc']['password'][CONFIG_LANG]
    clear_password: bpy.props.StringProperty(
        name='',
        description=desc,
        maxlen=128,
        default='',
        options={'SKIP_SAVE'},
        subtype='NONE',
    )

    desc = TRADUCTOR['desc']['toggle_password'][CONFIG_LANG]
    show_password: bpy.props.BoolProperty(
        name='',
        description=desc,
        default=False,
        update=switch_password_visibility,
        options={'SKIP_SAVE'}
    )

    desc = TRADUCTOR['desc']['remember_email'][CONFIG_LANG]
    remember_email: bpy.props.BoolProperty(
        name='',
        description=desc,
        default=conf_email != '',
    )

    #desc = TRADUCTOR['desc']['credits'][CONFIG_LANG]
    total_credits: bpy.props.IntProperty(
        name='',
        #   description=desc
        options={'HIDDEN', 'SKIP_SAVE'},
        update=lambda a, b: None,
    )

    firstname: bpy.props.StringProperty(
        default='',
        name='',
        description='',
        options={'HIDDEN', 'SKIP_SAVE'},
        update=lambda a, b: None,
    )

    lastname: bpy.props.StringProperty(
        default='',
        name='',
        description='',
        options={'HIDDEN', 'SKIP_SAVE'},
        update=lambda a, b: None,
    )

    @classmethod
    def register(cls):
        """Link to window manager so these settings are reset at launch"""
        bpy.types.WindowManager.tresorio_user_props = bpy.props.PointerProperty(
            type=cls,
            name='tresorio_user_props',
            options={'HIDDEN', 'SKIP_SAVE'}
        )

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.tresorio_user_props


def update_max_cost(prop, ctx):
    del prop
    form_fields = ctx.window_manager.tresorio_render_form
    user_credits = ctx.window_manager.tresorio_user_props.total_credits
    # TODO get the real prices for each pack (dict)
    # -> prices[form_fields.render_farms] * form_fields.timeout
    price_per_hour_TODO_REMOVE = 1.27
    if form_fields.timeout == 0:
        form_fields.max_cost = price_per_hour_TODO_REMOVE * user_credits
    else:
        form_fields.max_cost = price_per_hour_TODO_REMOVE * form_fields.timeout


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

    desc = TRADUCTOR['desc']['output_formats_list'][CONFIG_LANG]
    output_formats_list: bpy.props.EnumProperty(
        description=desc,
        name='',
        items=(
            ('PNG', 'PNG', ''),
        ),
        default='PNG'
    )

    desc = TRADUCTOR['desc']['render_farms'][CONFIG_LANG]
    render_farms: bpy.props.EnumProperty(
        description=desc,
        name='',
        items=(
            ('XS', 'XS', '10 CPU 2 GPU'),
            ('S', 'S', '20 CPU 4 GPU'),
            ('M', 'M', '40 CPU 8 GPU'),
            ('L', 'L', '80 CPU 16 GPU'),
        ),
        default='S',
        update=update_max_cost,
    )

    render_types: bpy.props.EnumProperty(
        description='TODO DESC',
        name='',
        items=(
            ('FRAME', 'Frame', 'TODO DESC', 'RESTRICT_RENDER_OFF', 0),
            ('ANIMATION', 'Animation', 'TODO DESC', 'RENDER_ANIMATION', 1),
        ),
        default='ANIMATION'
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

    max_cost: bpy.props.FloatProperty(
        min=0,
        description='',
        name='',
        default=12*1.27,  # TODO change that to the real default pack * default time price
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


class TresorioReportProps(bpy.types.PropertyGroup):

    login_in: bpy.props.BoolProperty(
        name='',
        description='',
        default=False,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    invalid_logs: bpy.props.BoolProperty(
        name='',
        description='',
        default=False,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

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

    fetched_user_info: bpy.props.BoolProperty(
        default=False,
        name='',
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
        del bpy.types.WindowManager.tresorio_report_props
