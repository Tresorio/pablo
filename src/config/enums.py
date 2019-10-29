from dataclasses import dataclass

@dataclass
class RenderStatus():
    FINISHED = 'FINISHED'
    RUNNING = 'RUNNING'
    STOPPING = 'STOPPING'
    LAUNCHING = 'LAUNCHING'
