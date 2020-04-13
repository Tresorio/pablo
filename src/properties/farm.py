from src.config.langs import TRADUCTOR, CONFIG_LANG
import bpy

class TresorioFarmProps(bpy.types.PropertyGroup):

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

    number_of_farmers: bpy.props.IntProperty(
        update=lambda a, b: None,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    units_per_farmer: bpy.props.IntProperty(
        update=lambda a, b: None,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    is_available: bpy.props.BoolProperty(
        options={'HIDDEN', 'SKIP_SAVE'},
        default=True
    )

    @classmethod
    def register(cls):
        """Link to window manager so these settings are reset at launch"""
        bpy.types.WindowManager.tresorio_farm_props = bpy.props.CollectionProperty(
            type=cls,
            name='tresorio_farm_props',
            options={'HIDDEN', 'SKIP_SAVE'},
        )
        bpy.types.WindowManager.tresorio_farm_props_index = bpy.props.IntProperty(
            default=-1,
            name='',
            description='',
            options={'HIDDEN', 'SKIP_SAVE'},
            update=lambda a, b: None,
        )
        bpy.types.WindowManager.tresorio_farm_props_old_index = bpy.props.IntProperty(
            default=-1,
            name='',
            description='',
            options={'HIDDEN', 'SKIP_SAVE'},
            update=lambda a, b: None,
        )


    @classmethod
    def unregister(cls):
        """Unregister the class from blender"""
        del bpy.types.WindowManager.tresorio_farm_props
