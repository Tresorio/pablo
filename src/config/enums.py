"""This module contains all the enums required by the plugin"""

from dataclasses import dataclass


@dataclass
class RenderStatus():
    """Status of a render"""
    LAUNCHING = 'STARTING'
    RUNNING = 'RUNNING'
    STOPPING = 'STOPPING'
    STOPPED = 'STOPPED'
    FINISHED = 'FINISHED'
    ERROR = 'ERROR'

@dataclass
class RenderTypes():
    """Type of a render"""
    ANIMATION = 'ANIMATION'
    FRAME = 'FRAME'
