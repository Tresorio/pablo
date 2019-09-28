import bpy
from typing import Dict, Any
from src.config.langs import TRADUCTOR, CONFIG_LANG

# {'id': '2b084a59-69de-4b7b-b9ed-0407c0dca46b',
#  'name': 'My_new_render',
#  'engine': 'EEVEE',
#  'timeout': 12,
#  'farm': 'xs',
#  'renderType': 'FRAME',
#  'outputFormat': 'PNG',
#  'finished': False,
#  'totalFragments': 1,
#  'finishedFragments': 0,
#  'launched': True,
#  'uptime': None,
#  'createdAt': '2019-09-28T07:05:28.000Z',
#  'userId': '325489ce-c442-4e46-bbde-4d7cfc4964ae'}

# {
#     [{
#         "name": "My_new_render",
#         "id": "6eb01bfa-da54-4307-957c-239522821b04",
#         "timeout": 12,
#         "uptime": None,
#         "status": "running",
#         "progression": 100,
#         "fragments": [
#             {
#                 "frameNumber": 2,
#                 "ip": "http://192.168.1.17:7777",
#                 "id": "712f43f1-f2c1-420b-bac7-ec589939f0c7"
#             },
#         ]
#     }]
# }


def update_renders_details_prop(res: Dict[str, Any]) -> None:
    render = bpy.context.window_manager.tresorio_renders_details.add()
    render.id = res['id']
    render.name = res['name']
    if 'progression' in res and res['progression'] == 100:
        render.is_finished = True#res['finished']
    else:
        render.progression = res['progression']


class TresorioRendersDetailsProps(bpy.types.PropertyGroup):
    # Internal
    id: bpy.props.StringProperty(lambda a, b: None)

    # Render specifics
    name: bpy.props.StringProperty(lambda a, b: None)
    engine: bpy.props.StringProperty(lambda a, b: None)
    farm: bpy.props.StringProperty(lambda a, b: None)
    timeout: bpy.props.IntProperty(lambda a, b: None)
    type: bpy.props.StringProperty(lambda a, b: None)
    output_format: bpy.props.StringProperty(lambda a, b: None)
    launched: bpy.props.BoolProperty(lambda a, b: None)

    # Advancement
    uptime: bpy.props.IntProperty(lambda a, b: None)
    is_finished: bpy.props.BoolProperty(lambda a, b: None)

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
    created_at: bpy.props.StringProperty(lambda a, b: None)
    render_frames_count: bpy.props.IntProperty(lambda a, b: None)

    # UI specific
    view_details: bpy.props.BoolProperty(lambda a, b: None)

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
