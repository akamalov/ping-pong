"""
Base Component class for the ECS system.

Components are pure data containers that hold state information for entities.
They should not contain any behavior or logic.
"""

from abc import ABC
from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Component(ABC):
    """
    Base class for all ECS components.
    
    Components are pure data containers that store entity state.
    They should be immutable when possible and contain no logic.
    
    The @dataclass_json decorator enables automatic JSON serialization
    for save/load functionality.
    """
    pass 