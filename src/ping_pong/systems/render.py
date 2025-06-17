"""
Render system for drawing entities to the screen.
"""

from typing import List, Set, Type, Dict, Optional
import pygame

from ..core.ecs import EntityID, System
from ..core.ecs.component import Component
from ..components.position import PositionComponent
from ..components.render import RenderComponent
from ..components.score import ScoreComponent
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
        
        # Score display settings
        pygame.font.init()
        self.score_font = pygame.font.Font(None, 72)  # Large font for scores
        self.game_over_font = pygame.font.Font(None, 48)  # Medium font for game over
        self.score_color = (255, 255, 255)  # White
        self.game_over_color = (255, 255, 0)  # Yellow
        self.winner_color = (0, 255, 0)  # Green
        
        # Score manager entity reference
        self.score_manager_entity = None
    
    def set_score_manager_entity(self, score_entity: EntityID) -> None:
        """Set the score manager entity for score display."""
        self.score_manager_entity = score_entity
    
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
        
        # Draw center line
        self._draw_center_line()
        
        # Render scores
        self._render_scores()
        
        # Render debug information if enabled
        if self.config.DEBUG_MODE:
            self._render_debug_info(dt, len(entities))
    
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
    
    def _render_scores(self) -> None:
        """Render the current scores on screen."""
        if not self.score_manager_entity:
            return
        
        score_comp = self.entity_manager.get_component(self.score_manager_entity, ScoreComponent)
        if not score_comp:
            return
        
        # Calculate positions for score display
        quarter_width = self.config.SCREEN_WIDTH // 4
        score_y = 80  # Distance from top of screen
        
        # Render Player 1 score (left side)
        player1_text = self.score_font.render(str(score_comp.player1_score), True, self.score_color)
        player1_rect = player1_text.get_rect()
        player1_rect.centerx = quarter_width
        player1_rect.centery = score_y
        self.screen.blit(player1_text, player1_rect)
        
        # Render Player 2 score (right side) 
        player2_text = self.score_font.render(str(score_comp.player2_score), True, self.score_color)
        player2_rect = player2_text.get_rect()
        player2_rect.centerx = self.config.SCREEN_WIDTH - quarter_width
        player2_rect.centery = score_y
        self.screen.blit(player2_text, player2_rect)
        
        # Render game over message if applicable
        if score_comp.game_over:
            self._render_game_over_message(score_comp)
    
    def _render_game_over_message(self, score_comp: ScoreComponent) -> None:
        """Render game over message and winner announcement."""
        center_x = self.config.SCREEN_WIDTH // 2
        center_y = self.config.SCREEN_HEIGHT // 2
        
        # Game Over text
        game_over_text = self.game_over_font.render("GAME OVER", True, self.game_over_color)
        game_over_rect = game_over_text.get_rect()
        game_over_rect.centerx = center_x
        game_over_rect.centery = center_y - 40
        self.screen.blit(game_over_text, game_over_rect)
        
        # Winner text
        if score_comp.winner:
            winner_text = self.game_over_font.render(f"Player {score_comp.winner} Wins!", True, self.winner_color)
            winner_rect = winner_text.get_rect()
            winner_rect.centerx = center_x
            winner_rect.centery = center_y + 10
            self.screen.blit(winner_text, winner_rect)
        
        # Instructions text
        instructions_font = pygame.font.Font(None, 32)
        instructions_text = instructions_font.render("Press R to restart or ESC to quit", True, self.score_color)
        instructions_rect = instructions_text.get_rect()
        instructions_rect.centerx = center_x
        instructions_rect.centery = center_y + 60
        self.screen.blit(instructions_text, instructions_rect)
    
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
        
        # Add score debug info if available
        if self.score_manager_entity:
            score_comp = self.entity_manager.get_component(self.score_manager_entity, ScoreComponent)
            if score_comp:
                debug_info.append(f"Scores: {score_comp.player1_score} - {score_comp.player2_score}")
                if score_comp.last_scorer:
                    debug_info.append(f"Last scorer: Player {score_comp.last_scorer}")
        
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