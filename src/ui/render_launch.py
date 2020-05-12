import bpy
import time
import math
from src.properties.farm import TresorioFarmProps
from src.services.backend import get_farms
from src.config.enums import RenderTypes
from src.properties.render_form import get_render_type
from src.config.langs import TRADUCTOR, CONFIG_LANG
from src.ui.popup import popup, alert
import functools

class TresorioFarmList(bpy.types.UIList):
    bl_idname = 'OBJECT_UL_TRESORIO_FARMS_LIST'

    @staticmethod
    def draw_item(self,
                  context: bpy.types.Context,
                  layout: bpy.types.UILayout,
                  data: bpy.types.WindowManager,
                  item: TresorioFarmProps,
                  icon: int,
                  active_data: bpy.types.WindowManager,
                  active_propname: str,
                  index: int
                  ) -> None:
        box = layout.box()
        box.enabled = item.is_available
        box.scale_x=0.5
        box.scale_y=0.5
        split = box.split()
        if item.gpu != 0:
            split.label(text=str(item.gpu))
        split.label(text=str(item.cpu))
        split.label(text=str(math.floor(item.ram / 1000))+" "+TRADUCTOR['field']['GB'][CONFIG_LANG])
        split.label(text=str(float("{:.2f}".format(item.cost))))

    def draw_filter(self, context, layout):
        pass

class TresorioRenderResumer(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_TRESORIO_RENDERING_RESUMER'
    bl_label = 'Tresorio Rendering Resumer'
    bl_parent_id = 'OBJECT_PT_TRESORIO_PANEL'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'output'
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls,
             context: bpy.types.Context
             ) -> bool:
        """Chose wether to render the renders panel or not"""
        return (context.window_manager.tresorio_user_props.is_logged and
            context.window_manager.tresorio_user_props.is_resuming_rendering)

    def draw(self, context):
        farms = bpy.context.window_manager.tresorio_farm_props
        index = bpy.context.window_manager.tresorio_farm_props_index

        # Render to restart and its informations
        render_index = context.window_manager.tresorio_renders_list_index
        render = context.window_manager.tresorio_renders_details[render_index]
        mode = render.mode
        number_of_frames = render.total_frames - render.rendered_frames
        name = render.name

        layout = self.layout
        layout.label(text=TRADUCTOR['field']['resuming_summary'][CONFIG_LANG].format(str(number_of_frames), ('s' if number_of_frames > 1 else ''), mode, name))
        layout.separator()
        available_farms_count = functools.reduce(lambda acc,val : acc + val.is_available, farms, 0)
        if len(farms) == 0:
            layout.label(text=TRADUCTOR['field']['optimizing'][CONFIG_LANG])
        else:

            if index >= 0 and index < len(farms) and not farms[index].is_available:
                bpy.context.window_manager.tresorio_farm_props_index = bpy.context.window_manager.tresorio_farm_props_old_index
                popup(TRADUCTOR['notif']['farm_not_available'][CONFIG_LANG], icon='ERROR')
            else:
                bpy.context.window_manager.tresorio_farm_props_old_index = index

            if available_farms_count == 0:
                layout.label(text=TRADUCTOR['field']['farms_unavailable'][CONFIG_LANG])
                layout.label(text=TRADUCTOR['field']['servers_try_again'][CONFIG_LANG])
            else:
                layout.label(text=TRADUCTOR['field']['select_farm'][CONFIG_LANG])
            layout.separator()
            header = layout.box().split()
            if farms[0].gpu != 0:
                header.label(text="Gpu")
            header.label(text="Cpu")
            header.label(text="RAM")
            header.label(text=TRADUCTOR['field']['cost_per_hour'][CONFIG_LANG])
            layout.template_list('OBJECT_UL_TRESORIO_FARMS_LIST',
                                'Farms_list',
                                context.window_manager,
                                'tresorio_farm_props',
                                context.window_manager,
                                'tresorio_farm_props_index',
                                rows=1,
                                maxrows=len(farms),
            )
        layout.separator()
        layout.separator()
        row = layout.row()
        row.operator('tresorio.cancelrendering')
        if len(farms) != 0 and available_farms_count != 0:
            row.operator('tresorio.launchresume')



class TresorioRenderLauncher(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_TRESORIO_RENDERING_LAUNCHER'
    bl_label = 'Tresorio Rendering Launcher'
    bl_parent_id = 'OBJECT_PT_TRESORIO_PANEL'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'output'
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls,
             context: bpy.types.Context
             ) -> bool:
        """Chose wether to render the renders panel or not"""
        return (context.window_manager.tresorio_user_props.is_logged and
            context.window_manager.tresorio_user_props.is_launching_rendering)

    def draw(self, context):
        farms = bpy.context.window_manager.tresorio_farm_props
        index = bpy.context.window_manager.tresorio_farm_props_index
        rendering_mode = bpy.context.window_manager.tresorio_user_props.rendering_mode
        number_of_frames = bpy.context.scene.tresorio_render_form.number_of_frames

        layout = self.layout
        layout.label(text=TRADUCTOR['field']['rendering_summary'][CONFIG_LANG].format(rendering_mode, str(number_of_frames), ('s' if number_of_frames > 1 else '')))
        layout.separator()
        available_farms_count = functools.reduce(lambda acc,val : acc + val.is_available, farms, 0)
        if len(farms) == 0:
            layout.label(text=TRADUCTOR['field']['optimizing'][CONFIG_LANG])
        else:

            if index >= 0 and index < len(farms) and not farms[index].is_available:
                bpy.context.window_manager.tresorio_farm_props_index = bpy.context.window_manager.tresorio_farm_props_old_index
                popup(TRADUCTOR['notif']['farm_not_available'][CONFIG_LANG], icon='ERROR')
            else:
                bpy.context.window_manager.tresorio_farm_props_old_index = index

            if available_farms_count == 0:
                layout.label(text=TRADUCTOR['field']['farms_unavailable'][CONFIG_LANG])
                layout.label(text=TRADUCTOR['field']['servers_try_again'][CONFIG_LANG])
            else:
                layout.label(text=TRADUCTOR['field']['select_farm'][CONFIG_LANG])
            layout.separator()
            header = layout.box().split()
            if farms[0].gpu != 0:
                header.label(text="Gpu")
            header.label(text="Cpu")
            header.label(text="RAM")
            header.label(text=TRADUCTOR['field']['cost_per_hour'][CONFIG_LANG])
            layout.template_list('OBJECT_UL_TRESORIO_FARMS_LIST',
                                'Farms_list',
                                context.window_manager,
                                'tresorio_farm_props',
                                context.window_manager,
                                'tresorio_farm_props_index',
                                rows=1,
                                maxrows=len(farms),
            )
        layout.separator()
        layout.separator()
        row = layout.row()
        row.operator('tresorio.cancelrendering')
        if len(farms) != 0 and available_farms_count != 0:
            row.operator('tresorio.launchrendering')
