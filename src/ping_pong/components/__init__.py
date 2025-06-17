"""
Game components for the ping-pong ECS system.

This module contains all the component types used in the game,
including position, velocity, rendering, collision, input, and score components.
"""

from .position import PositionComponent
from .velocity import VelocityComponent
from .render import RenderComponent
from .collision import CollisionComponent
from .input import InputComponent
from .score import ScoreComponent

__all__ = [
    "PositionComponent",
    "VelocityComponent", 
    "RenderComponent",
    "CollisionComponent",
    "InputComponent",
    "ScoreComponent"
] 