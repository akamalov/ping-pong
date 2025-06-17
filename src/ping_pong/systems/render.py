"""
Render system for drawing entities to the screen.
"""

from typing import List, Set, Type, Dict
import pygame

from ..core.ecs import EntityID, System
from ..core.ecs.component import Component
from ..components.position import PositionComponent
from ..components.render import RenderComponent
from ..core.ecs.entity_manager import EntityManager
from ..core.config import GameConfig


class RenderSystem(System):
    """
    System that renders entities to the screen.
    
    This system processes all entities with render components,
    sorts them by layer, and draws them to the pygame surface.
    """
    
    def __init__(self, entity_manager: EntityManager, config: GameConfig, screen: pygame.Surface):
        super().__init__()
        self.entity_manager = entity_manager
        self.config = config
        self.screen = screen
        self.priority = 100  # Late in the update cycle (after all logic)
        
        # Surface cache for render components
        self.surface_cache: Dict[int, pygame.Surface] = {}
        
        # Background color
        self.background_color = (0, 0, 0)  # Black
        
        # Debug rendering settings
        self.debug_font = None
        if config.DEBUG_MODE:
            pygame.font.init()
            self.debug_font = pygame.font.Font(None, 24)
    
    def get_required_components(self) -> Set[Type[Component]]:
        """Return the components required by this system."""
        return {PositionComponent, RenderComponent}
    
    def update(self, dt: float, entities: List[EntityID]) -> None:
        """
        Update rendering.
        
        Args:
            dt: Delta time since last frame in seconds
            entities: List of entities with required components
        """
        # Clear screen
        self.screen.fill(self.background_color)
        
        # Get renderable entities and sort by layer
        renderable_entities = self._get_renderable_entities(entities)
        renderable_entities.sort(key=lambda x: x[2].layer)  # Sort by layer
        
        # Render each entity
        for entity_id, position, render_comp in renderable_entities:
            if render_comp.visible:
                self._render_entity(entity_id, position, render_comp)
        
        # Render debug information if enabled
        if self.config.DEBUG_MODE:
            self._render_debug_info(dt, len(entities))
        
        # Draw center line
        self._draw_center_line()
    
    def _get_renderable_entities(self, entities: List[EntityID]) -> List[tuple]:
        """Get entities that can be rendered, with their components."""
        renderable = []
        
        for entity_id in entities:
            position = self.entity_manager.get_component(entity_id, PositionComponent)
            render_comp = self.entity_manager.get_component(entity_id, RenderComponent)
            
            if position and render_comp:
                renderable.append((entity_id, position, render_comp))
        
        return renderable
    
    def _render_entity(self, entity_id: EntityID, position: PositionComponent, 
                      render_comp: RenderComponent) -> None:
        """Render a single entity."""
        # Get or create surface for this render component
        surface = self._get_surface_for_render_component(render_comp)
        
        if surface:
            # Calculate render position (center-based)
            render_rect = surface.get_rect()
            render_rect.centerx = int(position.x)
            render_rect.centery = int(position.y)
            
            # Draw to screen
            self.screen.blit(surface, render_rect)
            
            # Draw collision box if debug mode is enabled
            if self.config.SHOW_COLLISION_BOXES:
                from ..components.collision import CollisionComponent
                collision_comp = self.entity_manager.get_component(entity_id, CollisionComponent)
                if collision_comp:
                    self._draw_collision_box(position, collision_comp)
    
    def _get_surface_for_render_component(self, render_comp: RenderComponent) -> pygame.Surface:
        """Get or create a surface for a render component."""
        # Check if surface needs to be recreated
        if render_comp.dirty or render_comp.surface is None:
            render_comp.surface = render_comp.create_surface()
            render_comp.dirty = False
        
        return render_comp.surface
    
    def _draw_center_line(self) -> None:
        """Draw the center line of the field."""
        center_x = self.config.SCREEN_WIDTH // 2
        line_color = (100, 100, 100)  # Dark gray
        
        # Draw dashed center line
        dash_length = 10
        gap_length = 5
        y = 0
        
        while y < self.config.SCREEN_HEIGHT:
            pygame.draw.line(
                self.screen,
                line_color,
                (center_x, y),
                (center_x, min(y + dash_length, self.config.SCREEN_HEIGHT)),
                2
            )
            y += dash_length + gap_length
    
    def _draw_collision_box(self, position: PositionComponent, collision_comp) -> None:
        """Draw collision box for debugging."""
        if collision_comp:
            rect = collision_comp.get_collision_rect(position.x, position.y)
            pygame.draw.rect(self.screen, (255, 0, 0), rect, 1)  # Red outline
    
    def _render_debug_info(self, dt: float, entity_count: int) -> None:
        """Render debug information."""
        if not self.debug_font:
            return
        
        debug_info = [
            f"FPS: {1/dt:.1f}" if dt > 0 else "FPS: --",
            f"Entities: {entity_count}",
            f"Screen: {self.config.SCREEN_WIDTH}x{self.config.SCREEN_HEIGHT}"
        ]
        
        y_offset = 10
        for info in debug_info:
            text_surface = self.debug_font.render(info, True, (255, 255, 255))
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 25
    
    def set_background_color(self, color: tuple) -> None:
        """Set the background color."""
        self.background_color = color
    
    def clear_surface_cache(self) -> None:
        """Clear the surface cache."""
        self.surface_cache.clear() 