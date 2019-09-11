import bpy
from src.utils.email import get_email_from_conf
from src.utils.password import switch_password_visibility
from src.config.langs import set_new_lang, TRADUCTOR, CONFIG_LANG, ALL_LANGS

class TresorioSettings(bpy.types.PropertyGroup):
    bl_idname = 'tresorio.settings'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'

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
        bpy.types.Scene.tresorio_settings = bpy.props.PointerProperty(
            type=cls,
            name='tresorio_settings',
            options={'HIDDEN', 'SKIP_SAVE'})

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.tresorio_settings
