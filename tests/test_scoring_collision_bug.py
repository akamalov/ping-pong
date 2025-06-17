"""
Test suite for the scoring mechanism collision bug.

This test suite documents and tests the issue where the collision system
prevents the ball from exiting the screen, thus preventing scoring.
"""

import sys
import os
import pygame
import unittest
from unittest.mock import Mock, patch, MagicMock

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


class TestScoringCollisionBug(unittest.TestCase):
    """Test suite documenting the collision bug that prevents scoring."""
    
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
    
    def tearDown(self):
        """Clean up after tests."""
        pass
    
    def test_ball_bounces_off_left_boundary_bug(self):
        """Test that demonstrates the bug: ball bounces off left boundary instead of exiting."""
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
        
        # BUG: The ball should exit the screen (position.x < 0) for scoring
        # but instead it bounces off the left boundary
        print(f"Ball position after collision: x={updated_position.x}, y={updated_position.y}")
        print(f"Ball velocity after collision: dx={updated_velocity.dx}, dy={updated_velocity.dy}")
        
        # Document the bug: ball position should be < 0 but it's been reset to boundary
        self.assertGreaterEqual(updated_position.x, 5.0, 
                               "BUG: Ball bounced off left boundary instead of exiting screen")
        
        # Document the bug: velocity should maintain direction but it's been reflected
        self.assertGreater(updated_velocity.dx, 0, 
                          "BUG: Ball velocity was reflected instead of maintaining leftward direction")
    
    def test_ball_bounces_off_right_boundary_bug(self):
        """Test that demonstrates the bug: ball bounces off right boundary instead of exiting."""
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
        
        # BUG: The ball should exit the screen (position.x > SCREEN_WIDTH) for scoring
        # but instead it bounces off the right boundary
        print(f"Ball position after collision: x={updated_position.x}, y={updated_position.y}")
        print(f"Ball velocity after collision: dx={updated_velocity.dx}, dy={updated_velocity.dy}")
        
        # Document the bug: ball position should be > SCREEN_WIDTH but it's been reset to boundary
        self.assertLessEqual(updated_position.x, 795.0, 
                            "BUG: Ball bounced off right boundary instead of exiting screen")
        
        # Document the bug: velocity should maintain direction but it's been reflected
        self.assertLess(updated_velocity.dx, 0, 
                       "BUG: Ball velocity was reflected instead of maintaining rightward direction")
    
    def test_ball_correctly_bounces_off_top_bottom_boundaries(self):
        """Test that ball correctly bounces off top and bottom boundaries (this should work)."""
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
        
        # This should work correctly: ball bounces off top
        self.assertGreaterEqual(updated_position.y, 5.0, "Ball should bounce off top boundary")
        self.assertGreater(updated_velocity.dy, 0, "Ball velocity should be reflected downward")
    
    def test_paddle_stays_within_boundaries(self):
        """Test that paddles correctly stay within screen boundaries."""
        # Create a paddle near the top boundary
        paddle_entity = self.entity_manager.create_entity()
        
        position = PositionComponent(x=50.0, y=5.0)  # Near top edge
        velocity = VelocityComponent(dx=0.0, dy=-200.0)  # Moving up
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
        
        # Paddle should be constrained within boundaries
        self.assertGreaterEqual(updated_position.y, 50.0, 
                               "Paddle should be constrained within top boundary")


class TestScoringMechanism(unittest.TestCase):
    """Test the actual scoring mechanism in the Game class."""
    
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
    
    def test_scoring_detection_left_side(self):
        """Test that _check_scoring detects when ball exits left side."""
        # Position ball off the left side of screen
        ball_pos = self.game.entity_manager.get_component(
            self.game.ball, PositionComponent)
        ball_pos.x = -10.0  # Ball is off-screen to the left
        
        initial_player2_score = self.game.player2_score
        
        # Check scoring
        self.game._check_scoring()
        
        # Player 2 should have scored
        self.assertEqual(self.game.player2_score, initial_player2_score + 1,
                        "Player 2 should score when ball exits left side")
    
    def test_scoring_detection_right_side(self):
        """Test that _check_scoring detects when ball exits right side."""
        # Position ball off the right side of screen
        ball_pos = self.game.entity_manager.get_component(
            self.game.ball, PositionComponent)
        ball_pos.x = self.game.config.SCREEN_WIDTH + 10.0  # Ball is off-screen to the right
        
        initial_player1_score = self.game.player1_score
        
        # Check scoring
        self.game._check_scoring()
        
        # Player 1 should have scored
        self.assertEqual(self.game.player1_score, initial_player1_score + 1,
                        "Player 1 should score when ball exits right side")
    
    def test_no_scoring_when_ball_within_bounds(self):
        """Test that no scoring occurs when ball is within screen bounds."""
        # Position ball within screen bounds
        ball_pos = self.game.entity_manager.get_component(
            self.game.ball, PositionComponent)
        ball_pos.x = self.game.config.SCREEN_WIDTH / 2  # Ball is in center
        
        initial_player1_score = self.game.player1_score
        initial_player2_score = self.game.player2_score
        
        # Check scoring
        self.game._check_scoring()
        
        # No scores should change
        self.assertEqual(self.game.player1_score, initial_player1_score,
                        "Player 1 score should not change when ball is within bounds")
        self.assertEqual(self.game.player2_score, initial_player2_score,
                        "Player 2 score should not change when ball is within bounds")


class TestIntegrationScoringFlow(unittest.TestCase):
    """Integration test for the complete scoring flow."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.config = GameConfig()
        self.config.SCREEN_WIDTH = 800
        self.config.SCREEN_HEIGHT = 600
        
        self.entity_manager = EntityManager()
        self.collision_system = CollisionSystem(self.entity_manager, self.config)
        self.entity_factory = EntityFactory(self.entity_manager, self.config)
    
    def test_full_scoring_flow_currently_broken(self):
        """Integration test showing the full broken scoring flow."""
        # Create a ball moving towards the left boundary
        ball_entity = self.entity_factory.create_ball(100.0, 300.0)
        
        # Get components and set initial velocity towards left boundary
        position = self.entity_manager.get_component(ball_entity, PositionComponent)
        velocity = self.entity_manager.get_component(ball_entity, VelocityComponent)
        velocity.set_velocity(-300.0, 0.0)  # Fast leftward velocity
        
        print(f"Initial ball state: pos=({position.x}, {position.y}), vel=({velocity.dx}, {velocity.dy})")
        
        # Simulate multiple frames to move ball to boundary
        for frame in range(10):
            # Update position based on velocity (movement system logic)
            dt = 1.0/60.0  # 60 FPS
            position.x += velocity.dx * dt
            position.y += velocity.dy * dt
            
            # Update collision system
            entities = [ball_entity]
            self.collision_system.update(dt, entities)
            
            print(f"Frame {frame + 1}: pos=({position.x:.1f}, {position.y:.1f}), vel=({velocity.dx:.1f}, {velocity.dy:.1f})")
            
            # Check if ball would have exited for scoring
            if position.x < 0:
                print(f"Ball should have scored on frame {frame + 1} but collision system prevented it")
                break
        
        # Final position should show the ball never exited the screen due to collision system
        final_position = self.entity_manager.get_component(ball_entity, PositionComponent)
        final_velocity = self.entity_manager.get_component(ball_entity, VelocityComponent)
        
        print(f"Final ball state: pos=({final_position.x:.1f}, {final_position.y:.1f}), vel=({final_velocity.dx:.1f}, {final_velocity.dy:.1f})")
        
        # Document the bug: ball should be off-screen but isn't
        self.assertGreaterEqual(final_position.x, 0, 
                               "BUG DOCUMENTED: Ball never exited screen due to collision system bouncing it back")
        
        # Document the bug: velocity should still be leftward but was reflected
        self.assertGreater(final_velocity.dx, 0, 
                          "BUG DOCUMENTED: Ball velocity was reflected, preventing scoring")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)