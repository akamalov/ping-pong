"""
Core game engine components.

This module contains the fundamental building blocks of the game engine,
including the ECS system, configuration management, and main game loop.
"""

from .game import Game
from .config import GameConfig

__all__ = ["Game", "GameConfig"] 