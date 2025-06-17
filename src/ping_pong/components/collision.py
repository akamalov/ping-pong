"""
Collision component for collision detection and response.
"""

from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Set
from enum import Enum
import pygame

from ..core.ecs.component import Component


class CollisionType(Enum):
    """Types of collision objects."""
    PADDLE = "paddle"
    BALL = "ball"
    WALL = "wall"
    GOAL = "goal"


@dataclass_json
@dataclass
class CollisionComponent(Component):
    """
    Component that handles collision detection and response.
    
    Attributes:
        width: Width of the collision box
        height: Height of the collision box
        collision_type: Type of collision object
        solid: Whether this object blocks movement
        trigger: Whether this is a trigger (detects but doesn't block)
        collision_mask: Set of collision types this object can collide with
        bounce_factor: How much velocity is retained after collision (0-1)
    """
    width: float = 10.0
    height: float = 10.0
    collision_type: CollisionType = CollisionType.PADDLE
    solid: bool = True
    trigger: bool = False
    bounce_factor: float = 1.0
    
    # Collision mask - which types this object can collide with
    # This is handled as a list for JSON serialization
    collision_mask: list = None
    
    def __post_init__(self):
        """Initialize collision mask if not provided."""
        if self.collision_mask is None:
            self.collision_mask = [ct.value for ct in CollisionType]
    
    def reset(self) -> None:
        """Reset to default collision state."""
        self.width = 10.0
        self.height = 10.0
        self.collision_type = CollisionType.PADDLE
        self.solid = True
        self.trigger = False
        self.bounce_factor = 1.0
        self.collision_mask = [ct.value for ct in CollisionType]
    
    def set_size(self, width: float, height: float) -> None:
        """Set the collision box size."""
        self.width = width
        self.height = height
    
    def can_collide_with(self, other_type: CollisionType) -> bool:
        """Check if this object can collide with another type."""
        return other_type.value in self.collision_mask
    
    def add_collision_type(self, collision_type: CollisionType) -> None:
        """Add a collision type to the mask."""
        if collision_type.value not in self.collision_mask:
            self.collision_mask.append(collision_type.value)
    
    def remove_collision_type(self, collision_type: CollisionType) -> None:
        """Remove a collision type from the mask."""
        if collision_type.value in self.collision_mask:
            self.collision_mask.remove(collision_type.value)
    
    def get_collision_rect(self, x: float, y: float) -> pygame.Rect:
        """Get the collision rectangle at the given position."""
        return pygame.Rect(
            int(x - self.width / 2),
            int(y - self.height / 2),
            int(self.width),
            int(self.height)
        )
    
    def get_collision_bounds(self, x: float, y: float) -> tuple:
        """Get collision bounds as (left, top, right, bottom)."""
        half_width = self.width / 2
        half_height = self.height / 2
        return (
            x - half_width,  # left
            y - half_height,  # top
            x + half_width,   # right
            y + half_height   # bottom
        )
    
    def __str__(self) -> str:
        return (f"Collision(type: {self.collision_type.value}, "
                f"size: {self.width}x{self.height}, "
                f"solid: {self.solid}, bounce: {self.bounce_factor})") 