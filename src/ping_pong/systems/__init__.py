"""
Game systems for the ping-pong game.

This module contains all the systems that process entities and their components.
Systems handle the game logic, rendering, input, collision detection, scoring, and more.
"""

from .movement import MovementSystem
from .collision import CollisionSystem
from .input import InputSystem
from .render import RenderSystem
from .score import ScoreSystem

__all__ = [
    "MovementSystem",
    "CollisionSystem", 
    "InputSystem",
    "RenderSystem",
    "ScoreSystem"
] 