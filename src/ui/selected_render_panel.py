import bpy
from src.config.langs import TRADUCTOR, CONFIG_LANG


class TresorioSelectedRenderPanel(bpy.types.Panel):
    bl_label = TRADUCTOR['field']['selected_render_details'][CONFIG_LANG]
    bl_idname = 'OBJECT_PT_TRESORIO_SELECTED_RENDER_PANEL'
    bl_parent_id = 'OBJECT_PT_TRESORIO_RENDERS_PANEL'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'

    def draw(self, context: bpy.types.Context):
        nb_renders = len(context.window_manager.tresorio_renders_details)
        layout = self.layout.split(factor=0.03)
        layout.row()
        box = layout.box()

        if nb_renders == 0:
            box.label(text=TRADUCTOR['field']['its_all_empty'][CONFIG_LANG])
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
            right.label(text=render.farm.upper())

            left.label(text=TRADUCTOR['field']['format'][CONFIG_LANG]+':')
            right.label(text=render.output_format.capitalize())
            

            left.label(text=TRADUCTOR['field']['uptime'][CONFIG_LANG]+':')
            right.label(text=str(render.uptime))
            
        # if render.is_finished is False:
