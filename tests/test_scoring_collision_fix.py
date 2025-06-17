"""
Test suite for the fixed scoring mechanism.

This test suite verifies that the collision system fix allows balls to exit
through left and right boundaries for scoring while maintaining proper
collision behavior for other entities and boundaries.
"""

import sys
import os
import pygame
import unittest
from unittest.mock import Mock, patch

# Add the source directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ping_pong.core.config import GameConfig
from ping_pong.core.ecs.entity_manager import EntityManager
from ping_pong.components.position import PositionComponent
from ping_pong.components.velocity import VelocityComponent
from ping_pong.components.collision import CollisionComponent, CollisionType
from ping_pong.systems.collision import CollisionSystem
from ping_pong.entities.entity_factory import EntityFactory
from ping_pong.core.game import Game


class TestScoringCollisionFix(unittest.TestCase):
    """Test suite verifying the collision system fix for scoring."""
    
    def setUp(self):
        """Set up test environment."""
        # Initialize pygame without display
        pygame.init()
        
        # Create test configuration
        self.config = GameConfig()
        self.config.SCREEN_WIDTH = 800
        self.config.SCREEN_HEIGHT = 600
        
        # Create entity manager and collision system
        self.entity_manager = EntityManager()
        self.collision_system = CollisionSystem(self.entity_manager, self.config)
        
        # Create entity factory
        self.entity_factory = EntityFactory(self.entity_manager, self.config)
    
    def test_ball_exits_left_boundary_for_scoring(self):
        """Test that ball can now exit left boundary for scoring."""
        # Create a ball at the left boundary moving left
        ball_entity = self.entity_manager.create_entity()
        
        # Position the ball at the left edge moving left
        position = PositionComponent(x=5.0, y=300.0)  # 5 pixels from left edge
        velocity = VelocityComponent(dx=-200.0, dy=0.0)  # Moving left at 200 px/s
        collision = CollisionComponent(
            width=10.0,
            height=10.0,
            collision_type=CollisionType.BALL,
            bounce_factor=1.0
        )
        
        self.entity_manager.add_component(ball_entity, position)
        self.entity_manager.add_component(ball_entity, velocity)
        self.entity_manager.add_component(ball_entity, collision)
        
        # Update collision system
        entities = [ball_entity]
        self.collision_system.update(0.1, entities)  # 0.1 second update
        
        # Get updated components
        updated_position = self.entity_manager.get_component(ball_entity, PositionComponent)
        updated_velocity = self.entity_manager.get_component(ball_entity, VelocityComponent)
        
        print(f"Ball position after collision: x={updated_position.x}, y={updated_position.y}")
        print(f"Ball velocity after collision: dx={updated_velocity.dx}, dy={updated_velocity.dy}")
        
        # FIX VERIFIED: Ball maintains position and velocity direction
        self.assertEqual(updated_position.x, 5.0, 
                        "Ball position should remain unchanged (not bounced back)")
        
        self.assertEqual(updated_velocity.dx, -200.0, 
                        "Ball velocity should maintain leftward direction (not reflected)")
    
    def test_ball_exits_right_boundary_for_scoring(self):
        """Test that ball can now exit right boundary for scoring."""
        # Create a ball at the right boundary moving right
        ball_entity = self.entity_manager.create_entity()
        
        # Position the ball at the right edge moving right
        position = PositionComponent(x=795.0, y=300.0)  # 5 pixels from right edge
        velocity = VelocityComponent(dx=200.0, dy=0.0)  # Moving right at 200 px/s
        collision = CollisionComponent(
            width=10.0,
            height=10.0,
            collision_type=CollisionType.BALL,
            bounce_factor=1.0
        )
        
        self.entity_manager.add_component(ball_entity, position)
        self.entity_manager.add_component(ball_entity, velocity)
        self.entity_manager.add_component(ball_entity, collision)
        
        # Update collision system
        entities = [ball_entity]
        self.collision_system.update(0.1, entities)  # 0.1 second update
        
        # Get updated components
        updated_position = self.entity_manager.get_component(ball_entity, PositionComponent)
        updated_velocity = self.entity_manager.get_component(ball_entity, VelocityComponent)
        
        print(f"Ball position after collision: x={updated_position.x}, y={updated_position.y}")
        print(f"Ball velocity after collision: dx={updated_velocity.dx}, dy={updated_velocity.dy}")
        
        # FIX VERIFIED: Ball maintains position and velocity direction
        self.assertEqual(updated_position.x, 795.0, 
                        "Ball position should remain unchanged (not bounced back)")
        
        self.assertEqual(updated_velocity.dx, 200.0, 
                        "Ball velocity should maintain rightward direction (not reflected)")
    
    def test_ball_still_bounces_off_top_bottom_boundaries(self):
        """Test that ball still correctly bounces off top and bottom boundaries."""
        # Test top boundary
        ball_entity = self.entity_manager.create_entity()
        
        position = PositionComponent(x=400.0, y=5.0)  # Near top edge
        velocity = VelocityComponent(dx=0.0, dy=-200.0)  # Moving up
        collision = CollisionComponent(
            width=10.0,
            height=10.0,
            collision_type=CollisionType.BALL,
            bounce_factor=1.0
        )
        
        self.entity_manager.add_component(ball_entity, position)
        self.entity_manager.add_component(ball_entity, velocity)
        self.entity_manager.add_component(ball_entity, collision)
        
        # Update collision system
        entities = [ball_entity]
        self.collision_system.update(0.1, entities)
        
        # Get updated components
        updated_position = self.entity_manager.get_component(ball_entity, PositionComponent)
        updated_velocity = self.entity_manager.get_component(ball_entity, VelocityComponent)
        
        # This should still work correctly: ball bounces off top
        self.assertGreaterEqual(updated_position.y, 5.0, "Ball should bounce off top boundary")
        self.assertGreater(updated_velocity.dy, 0, "Ball velocity should be reflected downward")
    
    def test_paddle_still_constrained_to_boundaries(self):
        """Test that paddles are still constrained within all screen boundaries."""
        # Test left boundary for paddle
        paddle_entity = self.entity_manager.create_entity()
        
        position = PositionComponent(x=5.0, y=300.0)  # Near left edge
        velocity = VelocityComponent(dx=-200.0, dy=0.0)  # Moving left
        collision = CollisionComponent(
            width=20.0,
            height=100.0,
            collision_type=CollisionType.PADDLE,
            bounce_factor=1.0
        )
        
        self.entity_manager.add_component(paddle_entity, position)
        self.entity_manager.add_component(paddle_entity, velocity)
        self.entity_manager.add_component(paddle_entity, collision)
        
        # Update collision system
        entities = [paddle_entity]
        self.collision_system.update(0.1, entities)
        
        # Get updated components
        updated_position = self.entity_manager.get_component(paddle_entity, PositionComponent)
        updated_velocity = self.entity_manager.get_component(paddle_entity, VelocityComponent)
        
        # Paddle should be constrained within boundaries
        self.assertGreaterEqual(updated_position.x, 10.0, 
                               "Paddle should be constrained within left boundary")
        self.assertGreater(updated_velocity.dx, 0, 
                          "Paddle velocity should be reflected away from boundary")


class TestIntegrationScoringFlowFixed(unittest.TestCase):
    """Integration test for the complete fixed scoring flow."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.config = GameConfig()
        self.config.SCREEN_WIDTH = 800
        self.config.SCREEN_HEIGHT = 600
        
        self.entity_manager = EntityManager()
        self.collision_system = CollisionSystem(self.entity_manager, self.config)
        self.entity_factory = EntityFactory(self.entity_manager, self.config)
    
    def test_full_scoring_flow_now_works(self):
        """Integration test showing the complete fixed scoring flow."""
        # Create a ball moving towards the left boundary
        ball_entity = self.entity_factory.create_ball(100.0, 300.0)
        
        # Get components and set initial velocity towards left boundary
        position = self.entity_manager.get_component(ball_entity, PositionComponent)
        velocity = self.entity_manager.get_component(ball_entity, VelocityComponent)
        velocity.set_velocity(-300.0, 0.0)  # Fast leftward velocity
        
        print(f"Initial ball state: pos=({position.x}, {position.y}), vel=({velocity.dx}, {velocity.dy})")
        
        # Simulate multiple frames to move ball past boundary
        ball_exited_screen = False
        for frame in range(15):  # More frames to ensure ball exits
            # Update position based on velocity (movement system logic)
            dt = 1.0/60.0  # 60 FPS
            position.x += velocity.dx * dt
            position.y += velocity.dy * dt
            
            # Update collision system
            entities = [ball_entity]
            self.collision_system.update(dt, entities)
            
            print(f"Frame {frame + 1}: pos=({position.x:.1f}, {position.y:.1f}), vel=({velocity.dx:.1f}, {velocity.dy:.1f})")
            
            # Check if ball has exited for scoring
            if position.x < 0:
                print(f"SUCCESS: Ball exited screen for scoring on frame {frame + 1}")
                ball_exited_screen = True
                break
        
        # Final position should show the ball exited the screen
        final_position = self.entity_manager.get_component(ball_entity, PositionComponent)
        final_velocity = self.entity_manager.get_component(ball_entity, VelocityComponent)
        
        print(f"Final ball state: pos=({final_position.x:.1f}, {final_position.y:.1f}), vel=({final_velocity.dx:.1f}, {final_velocity.dy:.1f})")
        
        # FIX VERIFIED: Ball successfully exited screen
        self.assertTrue(ball_exited_screen, 
                       "SUCCESS: Ball successfully exited screen for scoring")
        
        self.assertLess(final_position.x, 0, 
                       "SUCCESS: Ball position is off-screen for scoring detection")
        
        self.assertLess(final_velocity.dx, 0, 
                       "SUCCESS: Ball velocity maintained leftward direction")


class TestScoringMechanismWithFix(unittest.TestCase):
    """Test the scoring mechanism with the collision fix."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock pygame to avoid display requirements
        with patch('pygame.init'), patch('pygame.font.init'), patch('pygame.display.set_mode'):
            self.game = Game("config.json")
        
        # Mock the screen and other pygame dependencies
        self.game.screen = Mock()
        self.game.clock = Mock()
        self.game.clock.tick.return_value = 16  # 60 FPS
        
        # Initialize game entities
        self.game.initialize_game_entities()
    
    def test_full_game_scoring_integration(self):
        """Test full game scoring integration with collision fix."""
        # Set up ball moving towards left boundary
        ball_pos = self.game.entity_manager.get_component(
            self.game.ball, PositionComponent)
        ball_vel = self.game.entity_manager.get_component(
            self.game.ball, VelocityComponent)
        
        # Position near left boundary and set velocity
        ball_pos.x = 50.0
        ball_pos.y = 300.0
        ball_vel.set_velocity(-400.0, 0.0)  # Fast leftward
        
        initial_player2_score = self.game.player2_score
        
        # Simulate game updates until ball exits screen
        for frame in range(20):
            dt = 1.0/60.0
            self.game._update_game(dt)
            
            # Check if scoring occurred
            if self.game.player2_score > initial_player2_score:
                print(f"SCORING SUCCESS: Player 2 scored on frame {frame + 1}")
                break
        
        # Verify scoring occurred
        self.assertEqual(self.game.player2_score, initial_player2_score + 1,
                        "Player 2 should have scored when ball exited left side")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)