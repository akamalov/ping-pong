"""
Velocity component for entity movement.
"""

from dataclasses import dataclass
from dataclasses_json import dataclass_json
import math

from ..core.ecs.component import Component


@dataclass_json
@dataclass
class VelocityComponent(Component):
    """
    Component that stores the velocity of an entity in 2D space.
    
    Attributes:
        dx: Velocity in X direction (pixels per second)
        dy: Velocity in Y direction (pixels per second)
        max_speed: Maximum allowed speed (0 = no limit)
    """
    dx: float = 0.0
    dy: float = 0.0
    max_speed: float = 0.0  # 0 means no speed limit
    
    def reset(self) -> None:
        """Reset to zero velocity."""
        self.dx = 0.0
        self.dy = 0.0
    
    def set_velocity(self, dx: float, dy: float) -> None:
        """Set the velocity components."""
        self.dx = dx
        self.dy = dy
        self._clamp_to_max_speed()
    
    def add_velocity(self, dx: float, dy: float) -> None:
        """Add to the current velocity."""
        self.dx += dx
        self.dy += dy
        self._clamp_to_max_speed()
    
    def scale_velocity(self, factor: float) -> None:
        """Scale the velocity by a factor."""
        self.dx *= factor
        self.dy *= factor
        self._clamp_to_max_speed()
    
    def get_speed(self) -> float:
        """Get the current speed (magnitude of velocity)."""
        return math.sqrt(self.dx * self.dx + self.dy * self.dy)
    
    def get_direction(self) -> float:
        """Get the direction in radians."""
        return math.atan2(self.dy, self.dx)
    
    def set_speed_and_direction(self, speed: float, direction: float) -> None:
        """Set velocity using speed and direction."""
        self.dx = speed * math.cos(direction)
        self.dy = speed * math.sin(direction)
        self._clamp_to_max_speed()
    
    def normalize(self, target_speed: float = 1.0) -> None:
        """Normalize velocity to target speed."""
        current_speed = self.get_speed()
        if current_speed > 0:
            factor = target_speed / current_speed
            self.dx *= factor
            self.dy *= factor
    
    def reflect_x(self) -> None:
        """Reflect velocity horizontally (reverse X component)."""
        self.dx = -self.dx
    
    def reflect_y(self) -> None:
        """Reflect velocity vertically (reverse Y component)."""
        self.dy = -self.dy
    
    def _clamp_to_max_speed(self) -> None:
        """Clamp velocity to maximum speed if set."""
        if self.max_speed > 0:
            current_speed = self.get_speed()
            if current_speed > self.max_speed:
                factor = self.max_speed / current_speed
                self.dx *= factor
                self.dy *= factor
    
    def __str__(self) -> str:
        return f"Velocity({self.dx:.1f}, {self.dy:.1f}) [speed: {self.get_speed():.1f}]" 