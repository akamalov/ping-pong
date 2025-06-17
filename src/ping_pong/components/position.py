"""
Position component for entity positioning.
"""

from dataclasses import dataclass
from dataclasses_json import dataclass_json

from ..core.ecs.component import Component


@dataclass_json
@dataclass
class PositionComponent(Component):
    """
    Component that stores the position of an entity in 2D space.
    
    Attributes:
        x: X coordinate in pixels
        y: Y coordinate in pixels
    """
    x: float = 0.0
    y: float = 0.0
    
    def reset(self) -> None:
        """Reset to default position."""
        self.x = 0.0
        self.y = 0.0
    
    def set_position(self, x: float, y: float) -> None:
        """Set the position coordinates."""
        self.x = x
        self.y = y
    
    def translate(self, dx: float, dy: float) -> None:
        """Move the position by the given offset."""
        self.x += dx
        self.y += dy
    
    def distance_to(self, other: 'PositionComponent') -> float:
        """Calculate distance to another position."""
        dx = self.x - other.x
        dy = self.y - other.y
        return (dx * dx + dy * dy) ** 0.5
    
    def __str__(self) -> str:
        return f"Position({self.x:.1f}, {self.y:.1f})" 