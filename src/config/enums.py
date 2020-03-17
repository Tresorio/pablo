"""This module contains all the enums required by the plugin"""

from dataclasses import dataclass


@dataclass
class RenderStatus():
    """Status of a render"""
    FINISHED = 'FINISHED'
    RUNNING = 'RUNNING'
    STOPPING = 'STOPPING'
    LAUNCHING = 'LAUNCHING'
    ERROR = 'ERROR'
    REASSEMBLING = 'REASSEMBLING'


@dataclass
class RenderTypes():
    """Type of a render"""
    ANIMATION = 'ANIMATION'
    FRAME = 'FRAME'
