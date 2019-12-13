"""This module defines the download render results operator"""

from typing import Set

from src.config.langs import TRADUCTOR, CONFIG_LANG
from src.services.backend import download_render_results
import bpy


class TresorioDownloadRenderResultsOperator(bpy.types.Operator):
    """Download render result operator"""
    __doc__ = TRADUCTOR['desc']['download_render_results'][CONFIG_LANG]
    bl_idname = 'tresorio.download_render_results'
    bl_label = TRADUCTOR['field']['download_results'][CONFIG_LANG]

    index: bpy.props.IntProperty(options={'HIDDEN', 'SKIP_SAVE'})
    filter_glob: bpy.props.StringProperty(
        default='*.zip',
        name='',
        options={'HIDDEN', 'SKIP_SAVE'},
    )
    filepath: bpy.props.StringProperty(
        name='',
        description='',
        subtype='FILE_PATH',
        options={'HIDDEN', 'SKIP_SAVE'}
    )
    directory: bpy.props.StringProperty(
        name='',
        description='',
        subtype='FILE_PATH',
        options={'HIDDEN', 'SKIP_SAVE'}
    )

    def execute(self,
                context: bpy.types.Context
                ) -> Set[str]:
        """Called when operator is called"""
        render = context.window_manager.tresorio_renders_details[self.index]
        if self.filepath == '':
            self.filepath = render.name + '.zip'
        download_render_results(render, self.filepath)
        return {'FINISHED'}

    def invoke(self,
               context: bpy.types.Context,
               event: bpy.types.Event
               ) -> Set[str]:
        """Called when operator is called with 'INVOKE_DEFAULT'"""
        del event
        self.filepath = context.window_manager.tresorio_renders_details[self.index].name + '.zip'
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
