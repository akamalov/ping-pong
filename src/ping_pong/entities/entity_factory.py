"""
Entity factory for creating game entities.
"""

import random
import math

from ..core.ecs import EntityID
from ..core.ecs.entity_manager import EntityManager
from ..core.config import GameConfig
from ..components.position import PositionComponent
from ..components.velocity import VelocityComponent
from ..components.render import RenderComponent
from ..components.collision import CollisionComponent, CollisionType
from ..components.input import InputComponent


class EntityFactory:
    """
    Factory class for creating game entities.
    
    This class provides convenient methods for creating common game entities
    like paddles, balls, and UI elements with appropriate components.
    """
    
    def __init__(self, entity_manager: EntityManager, config: GameConfig):
        self.entity_manager = entity_manager
        self.config = config
        
        # Store component types for easy access
        self.position_component_type = PositionComponent
        self.velocity_component_type = VelocityComponent
        self.render_component_type = RenderComponent
        self.collision_component_type = CollisionComponent
        self.input_component_type = InputComponent
    
    def create_paddle(self, x: float, y: float, player_number: int = 1) -> EntityID:
        """
        Create a paddle entity.
        
        Args:
            x: X position
            y: Y position
            player_number: Player number (1 or 2) for input binding
            
        Returns:
            Entity ID of the created paddle
        """
        entity = self.entity_manager.create_entity()
        
        # Position component
        position = PositionComponent(x=x, y=y)
        self.entity_manager.add_component(entity, position)
        
        # Velocity component (paddles can move)
        velocity = VelocityComponent(
            dx=0.0, 
            dy=0.0, 
            max_speed=self.config.PADDLE_SPEED
        )
        self.entity_manager.add_component(entity, velocity)
        
        # Render component
        paddle_color = (255, 255, 255)  # White
        if player_number == 1:
            paddle_color = (100, 150, 255)  # Light blue
        elif player_number == 2:
            paddle_color = (255, 100, 100)  # Light red
        
        render = RenderComponent(
            width=self.config.PADDLE_WIDTH,
            height=self.config.PADDLE_HEIGHT,
            color=paddle_color,
            layer=1
        )
        self.entity_manager.add_component(entity, render)
        
        # Collision component
        collision = CollisionComponent(
            width=self.config.PADDLE_WIDTH,
            height=self.config.PADDLE_HEIGHT,
            collision_type=CollisionType.PADDLE,
            solid=True,
            bounce_factor=self.config.PADDLE_BOUNCE_FACTOR,
            collision_mask=[CollisionType.BALL.value]  # Only collide with balls
        )
        self.entity_manager.add_component(entity, collision)
        
        # Input component
        input_comp = InputComponent(
            enabled=True,
            move_speed=self.config.PADDLE_SPEED
        )
        input_comp.setup_default_bindings(player_number)
        self.entity_manager.add_component(entity, input_comp)
        
        return entity
    
    def create_ball(self, x: float, y: float) -> EntityID:
        """
        Create a ball entity.
        
        Args:
            x: X position
            y: Y position
            
        Returns:
            Entity ID of the created ball
        """
        entity = self.entity_manager.create_entity()
        
        # Position component
        position = PositionComponent(x=x, y=y)
        self.entity_manager.add_component(entity, position)
        
        # Velocity component with random initial direction
        angle = random.uniform(-math.pi/4, math.pi/4)  # Random angle ±45 degrees
        direction = random.choice([-1, 1])  # Random left or right
        
        initial_vx = direction * self.config.BALL_SPEED * math.cos(angle)
        initial_vy = self.config.BALL_SPEED * math.sin(angle)
        
        velocity = VelocityComponent(
            dx=initial_vx,
            dy=initial_vy,
            max_speed=self.config.MAX_BALL_SPEED
        )
        self.entity_manager.add_component(entity, velocity)
        
        # Render component
        render = RenderComponent(
            width=self.config.BALL_SIZE,
            height=self.config.BALL_SIZE,
            color=(255, 255, 255),  # White
            layer=2  # Above paddles
        )
        self.entity_manager.add_component(entity, render)
        
        # Collision component
        collision = CollisionComponent(
            width=self.config.BALL_SIZE,
            height=self.config.BALL_SIZE,
            collision_type=CollisionType.BALL,
            solid=False,  # Ball doesn't block movement
            bounce_factor=self.config.BALL_BOUNCE_FACTOR,
            collision_mask=[
                CollisionType.PADDLE.value,
                CollisionType.WALL.value
            ]
        )
        self.entity_manager.add_component(entity, collision)
        
        return entity
    
    def create_wall(self, x: float, y: float, width: float, height: float) -> EntityID:
        """
        Create a wall entity.
        
        Args:
            x: X position
            y: Y position
            width: Wall width
            height: Wall height
            
        Returns:
            Entity ID of the created wall
        """
        entity = self.entity_manager.create_entity()
        
        # Position component
        position = PositionComponent(x=x, y=y)
        self.entity_manager.add_component(entity, position)
        
        # Render component (invisible by default)
        render = RenderComponent(
            width=width,
            height=height,
            color=(100, 100, 100),  # Dark gray
            layer=0,
            visible=self.config.DEBUG_MODE  # Only visible in debug mode
        )
        self.entity_manager.add_component(entity, render)
        
        # Collision component
        collision = CollisionComponent(
            width=width,
            height=height,
            collision_type=CollisionType.WALL,
            solid=True,
            bounce_factor=self.config.WALL_BOUNCE_FACTOR,
            collision_mask=[CollisionType.BALL.value]
        )
        self.entity_manager.add_component(entity, collision)
        
        return entity
    
    def create_goal(self, x: float, y: float, width: float, height: float, 
                   player_number: int) -> EntityID:
        """
        Create a goal entity.
        
        Args:
            x: X position
            y: Y position
            width: Goal width
            height: Goal height
            player_number: Which player this goal belongs to
            
        Returns:
            Entity ID of the created goal
        """
        entity = self.entity_manager.create_entity()
        
        # Position component
        position = PositionComponent(x=x, y=y)
        self.entity_manager.add_component(entity, position)
        
        # Render component (invisible trigger)
        render = RenderComponent(
            width=width,
            height=height,
            color=(255, 0, 0) if player_number == 1 else (0, 0, 255),
            layer=0,
            visible=self.config.DEBUG_MODE,
            alpha=100
        )
        self.entity_manager.add_component(entity, render)
        
        # Collision component (trigger)
        collision = CollisionComponent(
            width=width,
            height=height,
            collision_type=CollisionType.GOAL,
            solid=False,
            trigger=True,
            bounce_factor=0.0,
            collision_mask=[CollisionType.BALL.value]
        )
        self.entity_manager.add_component(entity, collision)
        
        return entity
    
    def create_particle(self, x: float, y: float, vx: float, vy: float, 
                       color: tuple, lifetime: float) -> EntityID:
        """
        Create a particle entity for effects.
        
        Args:
            x: X position
            y: Y position
            vx: X velocity
            vy: Y velocity
            color: RGB color tuple
            lifetime: How long the particle should live in seconds
            
        Returns:
            Entity ID of the created particle
        """
        entity = self.entity_manager.create_entity()
        
        # Position component
        position = PositionComponent(x=x, y=y)
        self.entity_manager.add_component(entity, position)
        
        # Velocity component
        velocity = VelocityComponent(dx=vx, dy=vy)
        self.entity_manager.add_component(entity, velocity)
        
        # Render component
        render = RenderComponent(
            width=2.0,
            height=2.0,
            color=color,
            layer=3,  # Above everything else
            alpha=255
        )
        self.entity_manager.add_component(entity, render)
        
        # Note: In a full implementation, you'd add a LifetimeComponent
        # to handle automatic destruction after the lifetime expires
        
        return entity 