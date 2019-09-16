import bpy
from src.utils.email import get_email_from_conf
from src.utils.password import switch_password_visibility
from src.config.langs import set_new_lang, TRADUCTOR, CONFIG_LANG, ALL_LANGS


class TresorioUserProps(bpy.types.PropertyGroup):
    email = get_email_from_conf()

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

    desc = TRADUCTOR['desc']['mail'][CONFIG_LANG]
    email: bpy.props.StringProperty(
        name='',
        description=desc,
        maxlen=128,
        options={'SKIP_SAVE'},
        default=email,
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
        default=email != '',
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


class TresorioRenderFormProps(bpy.types.PropertyGroup):

    # TODO : desc traduction, register, unregister

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
            ('cycles', 'Cycles', ''),
            ('eevee', 'Eevee', ''),
        ),
        default='cycles'
    )

    desc = TRADUCTOR['desc']['output_formats_list'][CONFIG_LANG]
    output_formats_list: bpy.props.EnumProperty(
        description=desc,
        name='',
        items=(
            ('png', 'PNG', ''),
        ),
        default='png'
    )

    desc = TRADUCTOR['desc']['render_farms'][CONFIG_LANG]
    render_farms: bpy.props.EnumProperty(
        description=desc,
        name='',
        items=(
            ('xs', 'XS', '10 CPU 2 GPU'),
            ('s', 'S', '20 CPU 4 GPU'),
            ('m', 'M', '40 CPU 8 GPU'),
            ('l', 'L', '80 CPU 16 GPU'),
        ),
        default='s'
    )

    desc = TRADUCTOR['desc']['timeout'][CONFIG_LANG]
    timeout: bpy.props.IntProperty(
        min=0,
        description=desc,
        default=12,
        subtype='TIME',
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
