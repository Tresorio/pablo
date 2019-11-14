"""Draw the information of a selected render"""

from src.ui.icons import TresorioIconsLoader as til
from src.config.langs import TRADUCTOR, CONFIG_LANG
import bpy


def draw_selected_render(layout: bpy.types.UILayout,
                         context: bpy.types.Context
                         ) -> None:
    """Draw the information of a selected render"""
    nb_renders = len(context.window_manager.tresorio_renders_details)
    box_layout = layout.split(factor=0.03)
    box_layout.row()
    box = box_layout.box()
    render_index = context.window_manager.tresorio_renders_list_index

    if nb_renders == 0:
        box.label(text=TRADUCTOR['field']['its_all_empty'][CONFIG_LANG],
                  icon_value=til.icon('TRESORIO_SADFACE'))
    elif render_index < 0 or render_index >= nb_renders:
        box.label(text=TRADUCTOR['field']['no_selected_render'][CONFIG_LANG],
                  icon_value=til.icon('TRESORIO_SADFACE'))
    else:
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
        if render.total_frames == 1:
            suffix = TRADUCTOR['field']['frame_singular'][CONFIG_LANG]
            text = text = f'{render.rendered_frames} / {render.total_frames} {suffix}'
            right.label(text=text)
        else:
            suffix = TRADUCTOR['field']['frame_plural'][CONFIG_LANG]
            text = f'{render.rendered_frames} / {render.total_frames} {suffix}'
            right.label(text=text)
