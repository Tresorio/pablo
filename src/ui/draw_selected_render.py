"""Draw the information of a selected render"""

import math

import bpy
from bundle_modules import i18n

# TODO fix that in i18n and not here
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
        return pluralize(i18n.t('blender.day').format(days), days) + " " + pluralize(i18n.t('blender.hour').format(hours), hours)
    elif hours != 0:
        return pluralize(i18n.t('blender.hour').format(hours), hours) + " " + pluralize(i18n.t('blender.minute').format(minutes), minutes)
    elif minutes != 0:
        return pluralize(i18n.t('blender.minute').format(minutes), minutes) + " " + pluralize(i18n.t('blender.second').format(seconds), seconds)
    else:
        return pluralize(i18n.t('blender.second').format(seconds), seconds)

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
        box.label(text=i18n.t('blender.its-all-empty'))
    elif render_index < 0 or render_index >= nb_renders:
        box.label(text=i18n.t('blender.no-selected-render'))
    else:
        render = context.window_manager.tresorio_renders_details[render_index]

        box = box.split(factor=0.4)
        left = box.column()
        right = box.column()

        left.label(text=i18n.t('blender.project')+':')
        right.label(text=render.project_name.capitalize())

        left.label(text=i18n.t('blender.name')+':')
        right.label(text=render.name.capitalize())

        left.label(text=i18n.t('blender.status')+':')
        right.label(text=i18n.t(f'blender.{render.status}'))

        left.label(text=i18n.t('blender.engine')+':')
        right.label(text=render.engine.capitalize())

        left.label(text=i18n.t('blender.format')+':')
        right.label(text=render.output_format.capitalize())

        left.label(text=i18n.t('blender.advancement')+':')
        if render.total_frames == 1:
            # TODO fix that
            suffix = i18n.t('blender.frame-singular')
            text = text = f'{render.rendered_frames} / {render.total_frames} {suffix}'
            right.label(text=text)
        else:
            # TODO fix that
            suffix = i18n.t('blender.frame-plural')
            text = f'{render.rendered_frames} / {render.total_frames} {suffix}'
            right.label(text=text)

        left.label(text=i18n.t('blender.uptime')+':')
        right.label(text=format_uptime(render.uptime))

        left.label(text=i18n.t('blender.total-cost')+':')
        # TODO string for tresorio coins abreviation
        right.label(text=str(float("{:.2f}".format(render.total_cost)))+" Tc")

        left.label(text=i18n.t('blender.farm')+':')
        res_box = right.box().split()
        res_left = res_box.column()
        res_right = res_box.column()
        if render.gpu != 0:
            res_left.label(text='Gpu:')
            res_right.label(text=str(render.gpu))
        res_left.label(text='Cpu:')
        res_right.label(text=str(render.cpu))
        res_left.label(text='Ram:')
        res_right.label(text=str(math.floor(render.ram / 1000))+" "+i18n.t('blender.GB'))
        res_left.label(text=i18n.t('blender.cost')+':')
        # TODO fix that
        res_right.label(text=str(float("{:.2f}".format(render.cost)))+" Tc / h")
