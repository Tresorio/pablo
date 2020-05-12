"""Draw the information of a selected render"""

from src.ui.icons import TresorioIconsLoader as til
from src.config.langs import TRADUCTOR, CONFIG_LANG
import bpy
import math

def pluralize(string, number):
    if number == 0 or number == 1:
        return string
    return string + "s"

def format_uptime(uptime):
    days = math.floor(uptime / (60 * 60 * 24))
    uptime -= days * 60 * 60 * 24

    hours = math.floor(uptime / (60 * 60))
    uptime -= hours * 60 * 60

    minutes = math.floor(uptime / 60)
    uptime -= minutes * 60

    seconds = uptime

    if days != 0:
        return pluralize(TRADUCTOR['field']['day'][CONFIG_LANG].format(days), days) + " " + pluralize(TRADUCTOR['field']['hour'][CONFIG_LANG].format(hours), hours)
    elif hours != 0:
        return pluralize(TRADUCTOR['field']['hour'][CONFIG_LANG].format(hours), hours) + " " + pluralize(TRADUCTOR['field']['minute'][CONFIG_LANG].format(minutes), minutes)
    elif minutes != 0:
        return pluralize(TRADUCTOR['field']['minute'][CONFIG_LANG].format(minutes), minutes) + " " + pluralize(TRADUCTOR['field']['second'][CONFIG_LANG].format(seconds), seconds)
    else:
        return pluralize(TRADUCTOR['field']['second'][CONFIG_LANG].format(seconds), seconds)

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
        box.label(text=TRADUCTOR['field']['its_all_empty'][CONFIG_LANG])
    elif render_index < 0 or render_index >= nb_renders:
        box.label(text=TRADUCTOR['field']['no_selected_render'][CONFIG_LANG])
    else:
        render = context.window_manager.tresorio_renders_details[render_index]

        box = box.split(factor=0.4)
        left = box.column()
        right = box.column()

        left.label(text=TRADUCTOR['field']['project'][CONFIG_LANG]+':')
        right.label(text=render.project_name.capitalize())

        left.label(text=TRADUCTOR['field']['name'][CONFIG_LANG]+':')
        right.label(text=render.name.capitalize())

        left.label(text=TRADUCTOR['field']['status'][CONFIG_LANG]+':')
        right.label(text=TRADUCTOR['field'][render.status][CONFIG_LANG])

        left.label(text=TRADUCTOR['field']['engine'][CONFIG_LANG]+':')
        right.label(text=render.engine.capitalize())

        left.label(text=TRADUCTOR['field']['format'][CONFIG_LANG]+':')
        right.label(text=render.output_format.capitalize())

        left.label(text=TRADUCTOR['field']['advancement'][CONFIG_LANG]+':')
        if render.total_frames == 1:
            suffix = TRADUCTOR['field']['frame_singular'][CONFIG_LANG]
            text = text = f'{render.rendered_frames} / {render.total_frames} {suffix}'
            right.label(text=text)
        else:
            suffix = TRADUCTOR['field']['frame_plural'][CONFIG_LANG]
            text = f'{render.rendered_frames} / {render.total_frames} {suffix}'
            right.label(text=text)

        left.label(text=TRADUCTOR['field']['uptime'][CONFIG_LANG]+':')
        right.label(text=format_uptime(render.uptime))

        left.label(text=TRADUCTOR['field']['total_cost'][CONFIG_LANG]+':')
        right.label(text=str(float("{:.2f}".format(render.total_cost)))+" Tc")

        left.label(text=TRADUCTOR['field']['farm'][CONFIG_LANG]+':')
        res_box = right.box().split()
        res_left = res_box.column()
        res_right = res_box.column()
        if render.gpu != 0:
            res_left.label(text='Gpu:')
            res_right.label(text=str(render.gpu))
        res_left.label(text='Cpu:')
        res_right.label(text=str(render.cpu))
        res_left.label(text='Ram:')
        res_right.label(text=str(math.floor(render.ram / 1000))+" "+TRADUCTOR['field']['GB'][CONFIG_LANG])
        res_left.label(text=TRADUCTOR['field']['cost'][CONFIG_LANG]+':')
        res_right.label(text=str(float("{:.2f}".format(render.cost)))+" Tc / h")
