"""
Collision system for collision detection and response.
"""

from typing import List, Set, Type, Tuple
import pygame

from ..core.ecs import EntityID, System
from ..core.ecs.component import Component
from ..components.position import PositionComponent
from ..components.velocity import VelocityComponent
from ..components.collision import CollisionComponent, CollisionType
from ..core.ecs.entity_manager import EntityManager
from ..core.config import GameConfig


class CollisionSystem(System):
    """
    System that handles collision detection and response.
    
    This system processes all entities with collision components,
    detects collisions between them, and applies appropriate responses
    such as bouncing, stopping, or triggering events.
    """
    
    def __init__(self, entity_manager: EntityManager, config: GameConfig):
        super().__init__()
        self.entity_manager = entity_manager
        self.config = config
        self.priority = 20  # After movement, before rendering
        
        # Screen boundaries for wall collisions
        self.screen_bounds = pygame.Rect(0, 0, config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    
    def get_required_components(self) -> Set[Type[Component]]:
        """Return the components required by this system."""
        return {PositionComponent, CollisionComponent}
    
    def update(self, dt: float, entities: List[EntityID]) -> None:
        """
        Update collision detection and response.
        
        Args:
            dt: Delta time since last frame in seconds
            entities: List of entities with required components
        """
        # First handle boundary collisions (walls)
        self._handle_boundary_collisions(entities)
        
        # Then handle entity-to-entity collisions
        self._handle_entity_collisions(entities)
    
    def _handle_boundary_collisions(self, entities: List[EntityID]) -> None:
        """Handle collisions with screen boundaries."""
        for entity_id in entities:
            position = self.entity_manager.get_component(entity_id, PositionComponent)
            collision = self.entity_manager.get_component(entity_id, CollisionComponent)
            velocity = self.entity_manager.get_component(entity_id, VelocityComponent)
            
            if not (position and collision):
                continue
            
            # Get collision bounds
            left, top, right, bottom = collision.get_collision_bounds(position.x, position.y)
            
            # Check boundary collisions
            hit_boundary = False
            
            # For balls, allow them to go off left and right sides for scoring
            # Only bounce off top and bottom boundaries
            if collision.collision_type == CollisionType.BALL:
                # Top boundary
                if top <= 0:
                    position.y = collision.height / 2
                    if velocity:
                        velocity.reflect_y()
                        velocity.scale_velocity(collision.bounce_factor)
                    hit_boundary = True
                
                # Bottom boundary
                elif bottom >= self.config.SCREEN_HEIGHT:
                    position.y = self.config.SCREEN_HEIGHT - collision.height / 2
                    if velocity:
                        velocity.reflect_y()
                        velocity.scale_velocity(collision.bounce_factor)
                    hit_boundary = True
                
                # Note: No left/right boundary handling for balls - allow them to go off screen for scoring
            
            else:
                # For non-ball entities (like paddles), handle all boundaries normally
                # Left boundary
                if left <= 0:
                    position.x = collision.width / 2
                    if velocity:
                        velocity.reflect_x()
                        velocity.scale_velocity(collision.bounce_factor)
                    hit_boundary = True
                
                # Right boundary
                elif right >= self.config.SCREEN_WIDTH:
                    position.x = self.config.SCREEN_WIDTH - collision.width / 2
                    if velocity:
                        velocity.reflect_x()
                        velocity.scale_velocity(collision.bounce_factor)
                    hit_boundary = True
                
                # Top boundary
                if top <= 0:
                    position.y = collision.height / 2
                    if velocity:
                        velocity.reflect_y()
                        velocity.scale_velocity(collision.bounce_factor)
                    hit_boundary = True
                
                # Bottom boundary
                elif bottom >= self.config.SCREEN_HEIGHT:
                    position.y = self.config.SCREEN_HEIGHT - collision.height / 2
                    if velocity:
                        velocity.reflect_y()
                        velocity.scale_velocity(collision.bounce_factor)
                    hit_boundary = True
            
            # Keep paddles within screen bounds (additional safety for paddles)
            if collision.collision_type == CollisionType.PADDLE:
                if top < 0:
                    position.y = collision.height / 2
                elif bottom > self.config.SCREEN_HEIGHT:
                    position.y = self.config.SCREEN_HEIGHT - collision.height / 2
    
    def _handle_entity_collisions(self, entities: List[EntityID]) -> None:
        """Handle collisions between entities."""
        # Check all pairs of entities for collisions
        for i, entity_a in enumerate(entities):
            for entity_b in entities[i + 1:]:
                self._check_collision_pair(entity_a, entity_b)
    
    def _check_collision_pair(self, entity_a: EntityID, entity_b: EntityID) -> None:
        """Check collision between two specific entities."""
        # Get components for both entities
        pos_a = self.entity_manager.get_component(entity_a, PositionComponent)
        col_a = self.entity_manager.get_component(entity_a, CollisionComponent)
        vel_a = self.entity_manager.get_component(entity_a, VelocityComponent)
        
        pos_b = self.entity_manager.get_component(entity_b, PositionComponent)
        col_b = self.entity_manager.get_component(entity_b, CollisionComponent)
        vel_b = self.entity_manager.get_component(entity_b, VelocityComponent)
        
        if not (pos_a and col_a and pos_b and col_b):
            return
        
        # Check if these collision types can interact
        if not (col_a.can_collide_with(col_b.collision_type) and 
                col_b.can_collide_with(col_a.collision_type)):
            return
        
        # Get collision rectangles
        rect_a = col_a.get_collision_rect(pos_a.x, pos_a.y)
        rect_b = col_b.get_collision_rect(pos_b.x, pos_b.y)
        
        # Check for collision
        if rect_a.colliderect(rect_b):
            self._resolve_collision(
                entity_a, pos_a, col_a, vel_a,
                entity_b, pos_b, col_b, vel_b
            )
    
    def _resolve_collision(self, 
                          entity_a: EntityID, pos_a: PositionComponent, 
                          col_a: CollisionComponent, vel_a: VelocityComponent,
                          entity_b: EntityID, pos_b: PositionComponent,
                          col_b: CollisionComponent, vel_b: VelocityComponent) -> None:
        """Resolve collision between two entities."""
        
        # Ball-Paddle collision
        if ((col_a.collision_type == CollisionType.BALL and col_b.collision_type == CollisionType.PADDLE) or
            (col_a.collision_type == CollisionType.PADDLE and col_b.collision_type == CollisionType.BALL)):
            
            # Determine which is ball and which is paddle
            if col_a.collision_type == CollisionType.BALL:
                ball_pos, ball_vel, ball_col = pos_a, vel_a, col_a
                paddle_pos, paddle_vel, paddle_col = pos_b, vel_b, col_b
            else:
                ball_pos, ball_vel, ball_col = pos_b, vel_b, col_b
                paddle_pos, paddle_vel, paddle_col = pos_a, vel_a, col_a
            
            if ball_vel:
                # Calculate collision normal based on hit position on paddle
                hit_offset = (ball_pos.y - paddle_pos.y) / (paddle_col.height / 2)
                hit_offset = max(-1.0, min(1.0, hit_offset))  # Clamp to [-1, 1]
                
                # Reflect ball horizontally
                ball_vel.reflect_x()
                
                # Add vertical component based on hit position
                ball_vel.dy += hit_offset * 100  # Adjust this multiplier as needed
                
                # Apply bounce factor and speed increase
                ball_vel.scale_velocity(ball_col.bounce_factor * self.config.BALL_SPEED_INCREASE)
                
                # Clamp to maximum speed
                if ball_vel.get_speed() > self.config.MAX_BALL_SPEED:
                    ball_vel.normalize(self.config.MAX_BALL_SPEED)
                
                # Separate the ball from paddle to prevent sticking
                if ball_pos.x < paddle_pos.x:
                    ball_pos.x = paddle_pos.x - (paddle_col.width + ball_col.width) / 2 - 1
                else:
                    ball_pos.x = paddle_pos.x + (paddle_col.width + ball_col.width) / 2 + 1
        
        # Handle other collision types as needed
        # For now, just basic separation for solid objects
        elif col_a.solid and col_b.solid:
            # Simple separation - move objects apart
            dx = pos_a.x - pos_b.x
            dy = pos_a.y - pos_b.y
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance > 0:
                # Normalize separation vector
                dx /= distance
                dy /= distance
                
                # Calculate required separation
                sep_distance = (col_a.width + col_b.width) / 2 + 1
                
                # Move objects apart
                pos_a.x = pos_b.x + dx * sep_distance
                pos_a.y = pos_b.y + dy * sep_distance 