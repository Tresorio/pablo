import bpy
from src.config.enums import RenderStatus
from src.ui.icons import TresorioIconsLoader as til
from src.config.langs import TRADUCTOR, CONFIG_LANG


class TresorioSelectedRenderPanel(bpy.types.Panel):
    bl_label = TRADUCTOR['field']['selected_render_details'][CONFIG_LANG]
    bl_idname = 'OBJECT_PT_TRESORIO_SELECTED_RENDER_PANEL'
    bl_parent_id = 'OBJECT_PT_TRESORIO_RENDERS_PANEL'
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'output'

    def draw(self, context: bpy.types.Context):
        nb_renders = len(context.window_manager.tresorio_renders_details)
        layout = self.layout
        box_layout = self.layout.split(factor=0.03)
        box_layout.row()
        box = box_layout.box()

        if nb_renders == 0:
            box.label(text=TRADUCTOR['field']['its_all_empty'][CONFIG_LANG],
                      icon_value=til.icon('TRESORIO_SADFACE'))
        else:
            render_index = context.window_manager.tresorio_renders_list_index
            render = context.window_manager.tresorio_renders_details[render_index]

            box = box.split(factor=0.4)
            left = box.column()
            right = box.column()

            left.label(text=TRADUCTOR['field']['name'][CONFIG_LANG]+':')
            right.label(text=render.name)

            left.label(text=TRADUCTOR['field']['timeout'][CONFIG_LANG]+':')
            if render.timeout != 0:
                right.label(text=str(render.timeout)+' ' +
                            TRADUCTOR['field']['hours'][CONFIG_LANG])
            else:
                right.label(text=TRADUCTOR['field']
                            ['max_timeout'][CONFIG_LANG])

            left.label(text=TRADUCTOR['field']['engine'][CONFIG_LANG]+':')
            right.label(text=render.engine.capitalize())

            left.label(text=TRADUCTOR['field']['render_pack'][CONFIG_LANG]+':')
            farmers = TRADUCTOR['field']['farmer']['singular' if render.number_farmers ==
                                                   1 else 'plural'][CONFIG_LANG]
            right.label(
                text=f'{render.farm.capitalize()}  ({render.number_farmers} {farmers})')

            left.label(text=TRADUCTOR['field']['format'][CONFIG_LANG]+':')
            right.label(text=render.output_format.capitalize())

            left.label(text=TRADUCTOR['field']['uptime'][CONFIG_LANG]+':')
            right.label(text=str(render.uptime))

            left.label(text=TRADUCTOR['field']['advancement'][CONFIG_LANG]+':')
            suffix = TRADUCTOR['field']['frame_singular'][CONFIG_LANG] if render.total_frames == 1 else TRADUCTOR['field']['frame_plural'][CONFIG_LANG]
            right.label(
                text=f'{render.rendered_frames} / {render.total_frames} {suffix}')
            if render.status == RenderStatus.FINISHED:
                layout.operator('tresorio.download_render_logs', text=TRADUCTOR['field']['download_logs'][CONFIG_LANG], icon='FILE_TEXT')
