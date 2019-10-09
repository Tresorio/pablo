import bpy
from src.utils.email import get_email_from_conf
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
        default='tresorio',
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
    total_credits: bpy.props.FloatProperty(
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
