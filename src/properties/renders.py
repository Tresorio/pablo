import bpy
from typing import Dict, Any
from src.config.langs import TRADUCTOR, CONFIG_LANG


def update_renders_details_prop(res: Dict[str, Any]) -> None:
    # print(res)
    render = bpy.context.window_manager.tresorio_renders_details.add()
    render.id = res['id']
    render.name = res['name']
    render.timeout = res['timeout']
    render.type = res['renderType']
    render.engine = res['engine']
    render.farm = res['farm']
    render.output_format = res['outputFormat']
    render.status = res['status']
    render.total_frames = res['totalFragments']
    render.rendered_frames = res['finishedFragments']
    render.number_farmers = res['numberFarmers']
    render.progression = res['progression']
    render.uptime = res['uptime']


class TresorioRendersDetailsProps(bpy.types.PropertyGroup):
    # Internal
    id: bpy.props.StringProperty(update=lambda a, b: None)

    # Render specifics
    name: bpy.props.StringProperty(update=lambda a, b: None)
    number_farmers: bpy.props.IntProperty(update=lambda a, b: None)
    engine: bpy.props.StringProperty(update=lambda a, b: None)
    farm: bpy.props.StringProperty(update=lambda a, b: None)
    timeout: bpy.props.IntProperty(update=lambda a, b: None)
    type: bpy.props.StringProperty(update=lambda a, b: None)
    output_format: bpy.props.StringProperty(update=lambda a, b: None)
    launched: bpy.props.BoolProperty(update=lambda a, b: None)

    # Advancement
    total_frames: bpy.props.IntProperty(update=lambda a, b: None)
    rendered_frames: bpy.props.IntProperty(update=lambda a, b: None)
    uptime: bpy.props.IntProperty(update=lambda a, b: None)
    status: bpy.props.StringProperty(update=lambda a, b: None)

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
        )

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.tresorio_renders_details
