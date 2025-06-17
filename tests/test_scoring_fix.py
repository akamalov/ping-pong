"""
Tests to verify that the collision system fix allows proper scoring.
"""

import pytest
import pygame
from unittest.mock import Mock, patch
import sys
import os

# Add src to path so we can import the game modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ping_pong.core.config import GameConfig
from ping_pong.components.position import PositionComponent
from ping_pong.components.velocity import VelocityComponent
from ping_pong.components.collision import CollisionComponent, CollisionType
from ping_pong.systems.collision import CollisionSystem


class TestCollisionSystemFix:
    """Test that the collision system fix allows proper scoring."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        config = GameConfig()
        config.SCREEN_WIDTH = 800
        config.SCREEN_HEIGHT = 600
        return config
    
    @pytest.fixture
    def collision_system(self, config):
        """Create a collision system for testing."""
        entity_manager = Mock()
        return CollisionSystem(entity_manager, config)
    
    def test_ball_does_not_bounce_off_left_boundary(self, collision_system, config):
        """Test that ball can now go off left boundary for scoring."""
        # Create mock components
        position = PositionComponent(x=-5, y=300)  # Ball past left edge
        velocity = VelocityComponent(dx=-100, dy=0)  # Moving left
        collision = CollisionComponent(
            width=10, height=10, 
            collision_type=CollisionType.BALL, 
            bounce_factor=1.0
        )
        
        initial_x = position.x
        initial_vx = velocity.dx
        
        # Mock entity manager
        collision_system.entity_manager.get_component.side_effect = lambda entity_id, component_type: {
            PositionComponent: position,
            VelocityComponent: velocity,
            CollisionComponent: collision
        }.get(component_type)
        
        # Process boundary collision
        collision_system._handle_boundary_collisions([1])
        
        # Ball should NOT be repositioned or have velocity reflected
        assert position.x == initial_x  # Ball position unchanged
        assert velocity.dx == initial_vx  # Velocity unchanged (still moving left)
    
    def test_ball_does_not_bounce_off_right_boundary(self, collision_system, config):
        """Test that ball can now go off right boundary for scoring."""
        # Create mock components
        position = PositionComponent(x=config.SCREEN_WIDTH + 5, y=300)  # Ball past right edge
        velocity = VelocityComponent(dx=100, dy=0)  # Moving right
        collision = CollisionComponent(
            width=10, height=10, 
            collision_type=CollisionType.BALL, 
            bounce_factor=1.0
        )
        
        initial_x = position.x
        initial_vx = velocity.dx
        
        # Mock entity manager
        collision_system.entity_manager.get_component.side_effect = lambda entity_id, component_type: {
            PositionComponent: position,
            VelocityComponent: velocity,
            CollisionComponent: collision
        }.get(component_type)
        
        # Process boundary collision
        collision_system._handle_boundary_collisions([1])
        
        # Ball should NOT be repositioned or have velocity reflected
        assert position.x == initial_x  # Ball position unchanged
        assert velocity.dx == initial_vx  # Velocity unchanged (still moving right)
    
    def test_ball_still_bounces_off_top_boundary(self, collision_system, config):
        """Test that ball still bounces off top boundary."""
        # Create mock components
        position = PositionComponent(x=400, y=-5)  # Ball past top edge
        velocity = VelocityComponent(dx=50, dy=-100)  # Moving up
        collision = CollisionComponent(
            width=10, height=10, 
            collision_type=CollisionType.BALL, 
            bounce_factor=1.0
        )
        
        # Mock entity manager
        collision_system.entity_manager.get_component.side_effect = lambda entity_id, component_type: {
            PositionComponent: position,
            VelocityComponent: velocity,
            CollisionComponent: collision
        }.get(component_type)
        
        # Process boundary collision
        collision_system._handle_boundary_collisions([1])
        
        # Ball should be repositioned and Y velocity reflected
        assert position.y > 0  # Ball moved back into bounds
        assert velocity.dy > 0  # Y velocity reflected (now moving down)
        assert velocity.dx == 50  # X velocity unchanged
    
    def test_ball_still_bounces_off_bottom_boundary(self, collision_system, config):
        """Test that ball still bounces off bottom boundary."""
        # Create mock components
        position = PositionComponent(x=400, y=config.SCREEN_HEIGHT + 5)  # Ball past bottom edge
        velocity = VelocityComponent(dx=-50, dy=100)  # Moving down
        collision = CollisionComponent(
            width=10, height=10, 
            collision_type=CollisionType.BALL, 
            bounce_factor=1.0
        )
        
        # Mock entity manager
        collision_system.entity_manager.get_component.side_effect = lambda entity_id, component_type: {
            PositionComponent: position,
            VelocityComponent: velocity,
            CollisionComponent: collision
        }.get(component_type)
        
        # Process boundary collision
        collision_system._handle_boundary_collisions([1])
        
        # Ball should be repositioned and Y velocity reflected
        assert position.y < config.SCREEN_HEIGHT  # Ball moved back into bounds
        assert velocity.dy < 0  # Y velocity reflected (now moving up)
        assert velocity.dx == -50  # X velocity unchanged
    
    def test_paddle_still_bounces_off_all_boundaries(self, collision_system, config):
        """Test that paddles still bounce off all boundaries (including left/right)."""
        # Test left boundary
        position = PositionComponent(x=-5, y=300)  # Paddle past left edge
        velocity = VelocityComponent(dx=-50, dy=0)  # Moving left
        collision = CollisionComponent(
            width=10, height=60, 
            collision_type=CollisionType.PADDLE, 
            bounce_factor=1.0
        )
        
        # Mock entity manager
        collision_system.entity_manager.get_component.side_effect = lambda entity_id, component_type: {
            PositionComponent: position,
            VelocityComponent: velocity,
            CollisionComponent: collision
        }.get(component_type)
        
        # Process boundary collision
        collision_system._handle_boundary_collisions([1])
        
        # Paddle should be repositioned and velocity reflected
        assert position.x > 0  # Paddle moved back into bounds
        assert velocity.dx > 0  # Velocity reflected (now moving right)
    
    def test_scoring_conditions_now_possible(self, collision_system, config):
        """Test that scoring conditions are now possible - balls can stay off-screen."""
        # Ball way off left side
        position = PositionComponent(x=-50, y=300)  # Ball far past left edge
        velocity = VelocityComponent(dx=-100, dy=0)  # Moving left
        collision = CollisionComponent(
            width=10, height=10, 
            collision_type=CollisionType.BALL, 
            bounce_factor=1.0
        )
        
        # Mock entity manager
        collision_system.entity_manager.get_component.side_effect = lambda entity_id, component_type: {
            PositionComponent: position,
            VelocityComponent: velocity,
            CollisionComponent: collision
        }.get(component_type)
        
        # Process boundary collision multiple times
        collision_system._handle_boundary_collisions([1])
        collision_system._handle_boundary_collisions([1])
        collision_system._handle_boundary_collisions([1])
        
        # Ball should remain off-screen, allowing scoring detection
        assert position.x < 0  # Ball is still off-screen (scoring condition maintained)
        assert velocity.dx < 0  # Still moving left (not bounced back)


if __name__ == "__main__":
    pytest.main([__file__])