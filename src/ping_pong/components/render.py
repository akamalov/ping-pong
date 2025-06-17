"""
Render component for entity rendering.
"""

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional, Tuple
import pygame

from ..core.ecs.component import Component


@dataclass_json
@dataclass
class RenderComponent(Component):
    """
    Component that stores rendering information for an entity.
    
    Attributes:
        width: Width of the rendered object
        height: Height of the rendered object
        color: RGB color tuple for simple colored rectangles
        layer: Rendering layer (higher values render on top)
        visible: Whether the entity should be rendered
        texture_name: Name of texture asset (if using textures)
        alpha: Transparency (0-255, 255 = opaque)
    """
    width: float = 10.0
    height: float = 10.0
    color: Tuple[int, int, int] = (255, 255, 255)  # White by default
    layer: int = 0
    visible: bool = True
    texture_name: Optional[str] = None
    alpha: int = 255
    
    # Runtime fields (not serialized)
    surface: Optional[pygame.Surface] = field(default=None, init=False)
    dirty: bool = field(default=True, init=False)
    
    def reset(self) -> None:
        """Reset to default render state."""
        self.width = 10.0
        self.height = 10.0
        self.color = (255, 255, 255)
        self.layer = 0
        self.visible = True
        self.texture_name = None
        self.alpha = 255
        self.surface = None
        self.dirty = True
    
    def set_color(self, r: int, g: int, b: int) -> None:
        """Set the color and mark as dirty."""
        self.color = (r, g, b)
        self.dirty = True
    
    def set_size(self, width: float, height: float) -> None:
        """Set the size and mark as dirty."""
        self.width = width
        self.height = height
        self.dirty = True
    
    def set_alpha(self, alpha: int) -> None:
        """Set the alpha transparency (0-255)."""
        self.alpha = max(0, min(255, alpha))
        self.dirty = True
    
    def set_texture(self, texture_name: str) -> None:
        """Set the texture name and mark as dirty."""
        self.texture_name = texture_name
        self.dirty = True
    
    def hide(self) -> None:
        """Hide the entity."""
        self.visible = False
    
    def show(self) -> None:
        """Show the entity."""
        self.visible = True
    
    def get_rect(self, x: float, y: float) -> pygame.Rect:
        """Get the rendering rectangle at the given position."""
        return pygame.Rect(
            int(x - self.width / 2),
            int(y - self.height / 2),
            int(self.width),
            int(self.height)
        )
    
    def create_surface(self) -> pygame.Surface:
        """Create a pygame surface for this render component."""
        if self.texture_name:
            # In a full implementation, this would load from asset manager
            # For now, create a colored rectangle
            surface = pygame.Surface((int(self.width), int(self.height)))
            surface.fill(self.color)
        else:
            # Create colored rectangle
            surface = pygame.Surface((int(self.width), int(self.height)))
            surface.fill(self.color)
        
        if self.alpha < 255:
            surface.set_alpha(self.alpha)
        
        return surface
    
    def __str__(self) -> str:
        return (f"Render(size: {self.width}x{self.height}, "
                f"color: {self.color}, layer: {self.layer}, "
                f"visible: {self.visible})") 