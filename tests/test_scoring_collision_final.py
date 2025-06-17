"""
Final comprehensive test suite for the scoring mechanism fix.

This test suite verifies that the collision system fix allows proper scoring
in realistic game scenarios while maintaining all other collision behaviors.
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
from ping_pong.systems.movement import MovementSystem
from ping_pong.entities.entity_factory import EntityFactory
from ping_pong.core.game import Game


class TestScoringSystemComplete(unittest.TestCase):
    """Complete test suite for the scoring system."""
    
    def setUp(self):
        """Set up test environment."""
        pygame.init()
        self.config = GameConfig()
        self.config.SCREEN_WIDTH = 800
        self.config.SCREEN_HEIGHT = 600
        
        self.entity_manager = EntityManager()
        self.collision_system = CollisionSystem(self.entity_manager, self.config)
        self.movement_system = MovementSystem(self.entity_manager)
        self.entity_factory = EntityFactory(self.entity_manager, self.config)
    
    def test_ball_exits_left_for_scoring_detailed(self):
        """Detailed test of ball exiting left boundary."""
        ball_entity = self.entity_factory.create_ball(10.0, 300.0)
        
        position = self.entity_manager.get_component(ball_entity, PositionComponent)
        velocity = self.entity_manager.get_component(ball_entity, VelocityComponent)
        collision = self.entity_manager.get_component(ball_entity, CollisionComponent)
        
        # Set up ball moving left at boundary
        position.x = 3.0  # Very close to left edge
        velocity.set_velocity(-100.0, 0.0)
        
        print(f"Initial: pos=({position.x}, {position.y}), vel=({velocity.dx}, {velocity.dy})")
        
        # Single update should allow ball to maintain trajectory
        entities = [ball_entity]
        self.collision_system.update(0.1, entities)
        
        print(f"After collision: pos=({position.x}, {position.y}), vel=({velocity.dx}, {velocity.dy})")
        
        # Ball should maintain its leftward trajectory
        self.assertEqual(position.x, 3.0, "Ball position unchanged by collision system")
        self.assertEqual(velocity.dx, -100.0, "Ball velocity unchanged by collision system")
        
        # Now apply movement to actually move the ball
        self.movement_system.update(0.05, entities)  # 0.05 seconds = 5 pixels left
        
        print(f"After movement: pos=({position.x}, {position.y}), vel=({velocity.dx}, {velocity.dy})")
        
        # Ball should now be off-screen for scoring
        self.assertLess(position.x, 0, "Ball should be off-screen for scoring detection")
    
    def test_ball_exits_right_for_scoring_detailed(self):
        """Detailed test of ball exiting right boundary."""
        ball_entity = self.entity_factory.create_ball(790.0, 300.0)
        
        position = self.entity_manager.get_component(ball_entity, PositionComponent)
        velocity = self.entity_manager.get_component(ball_entity, VelocityComponent)
        
        # Set up ball moving right at boundary
        position.x = 797.0  # Very close to right edge (screen width = 800)
        velocity.set_velocity(100.0, 0.0)
        
        print(f"Initial: pos=({position.x}, {position.y}), vel=({velocity.dx}, {velocity.dy})")
        
        # Apply collision system
        entities = [ball_entity]
        self.collision_system.update(0.1, entities)
        
        print(f"After collision: pos=({position.x}, {position.y}), vel=({velocity.dx}, {velocity.dy})")
        
        # Ball should maintain its rightward trajectory
        self.assertEqual(position.x, 797.0, "Ball position unchanged by collision system")
        self.assertEqual(velocity.dx, 100.0, "Ball velocity unchanged by collision system")
        
        # Apply movement to move the ball off-screen
        self.movement_system.update(0.05, entities)  # 0.05 seconds = 5 pixels right
        
        print(f"After movement: pos=({position.x}, {position.y}), vel=({velocity.dx}, {velocity.dy})")
        
        # Ball should now be off-screen for scoring
        self.assertGreater(position.x, self.config.SCREEN_WIDTH, 
                          "Ball should be off-screen for scoring detection")
    
    def test_ball_bounces_off_top_bottom_still_works(self):
        """Verify that top/bottom bouncing still works correctly."""
        ball_entity = self.entity_factory.create_ball(400.0, 10.0)
        
        position = self.entity_manager.get_component(ball_entity, PositionComponent)
        velocity = self.entity_manager.get_component(ball_entity, VelocityComponent)
        collision = self.entity_manager.get_component(ball_entity, CollisionComponent)
        
        # Set up ball hitting top boundary
        position.y = 3.0  # Close to top
        velocity.set_velocity(0.0, -100.0)  # Moving up
        
        print(f"Initial: pos=({position.x}, {position.y}), vel=({velocity.dx}, {velocity.dy})")
        
        # Apply collision system
        entities = [ball_entity]
        self.collision_system.update(0.1, entities)
        
        print(f"After collision: pos=({position.x}, {position.y}), vel=({velocity.dx}, {velocity.dy})")
        
        # Ball should have bounced off top boundary
        self.assertGreaterEqual(position.y, collision.height / 2, 
                               "Ball should be repositioned inside boundary")
        self.assertGreater(velocity.dy, 0, "Ball velocity should be reflected downward")
    
    def test_paddle_boundary_constraints_still_work(self):
        """Verify that paddle boundary constraints still work."""
        paddle_entity = self.entity_factory.create_paddle(10.0, 300.0, player_number=1)
        
        position = self.entity_manager.get_component(paddle_entity, PositionComponent)
        velocity = self.entity_manager.get_component(paddle_entity, VelocityComponent)
        collision = self.entity_manager.get_component(paddle_entity, CollisionComponent)
        
        # Set up paddle hitting left boundary
        position.x = 5.0  # Close to left edge
        velocity.set_velocity(-100.0, 0.0)  # Moving left
        
        print(f"Initial: pos=({position.x}, {position.y}), vel=({velocity.dx}, {velocity.dy})")
        
        # Apply collision system
        entities = [paddle_entity]
        self.collision_system.update(0.1, entities)
        
        print(f"After collision: pos=({position.x}, {position.y}), vel=({velocity.dx}, {velocity.dy})")
        
        # Paddle should be constrained within boundary
        self.assertGreaterEqual(position.x, collision.width / 2, 
                               "Paddle should be constrained within left boundary")
        self.assertGreater(velocity.dx, 0, "Paddle velocity should be reflected away from boundary")


class TestGameScoringIntegration(unittest.TestCase):
    """Integration test for game scoring with real Game class."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock pygame components but keep game logic intact
        with patch('pygame.display.set_mode'), \
             patch('pygame.display.set_caption'), \
             patch('pygame.time.Clock'):
            
            self.game = Game("config.json")
        
        # Mock screen to avoid rendering issues in tests
        self.game.screen = Mock()
        
        # Initialize entities
        self.game.initialize_game_entities()
    
    def test_scoring_when_ball_exits_left(self):
        """Test scoring when ball exits left side of screen."""
        # Get ball components
        ball_pos = self.game.entity_manager.get_component(self.game.ball, PositionComponent)
        ball_vel = self.game.entity_manager.get_component(self.game.ball, VelocityComponent)
        
        # Position ball near left boundary
        ball_pos.x = 15.0
        ball_pos.y = 300.0
        ball_vel.set_velocity(-500.0, 0.0)  # Fast leftward velocity
        
        initial_p2_score = self.game.player2_score
        
        print(f"Initial ball position: ({ball_pos.x}, {ball_pos.y})")
        print(f"Initial Player 2 score: {initial_p2_score}")
        
        # Simulate several game updates
        scored = False
        for frame in range(10):
            dt = 1.0/60.0  # 60 FPS
            
            # Update movement system (moves ball based on velocity)
            movement_entities = self.game.system_manager.get_entities_with_components(
                {PositionComponent, VelocityComponent})
            self.game.system_manager.get_system(MovementSystem).update(dt, movement_entities)
            
            # Update collision system (handles boundary logic)
            collision_entities = self.game.system_manager.get_entities_with_components(
                {PositionComponent, CollisionComponent})
            self.game.system_manager.get_system(CollisionSystem).update(dt, collision_entities)
            
            # Check for scoring
            self.game._check_scoring()
            
            print(f"Frame {frame + 1}: Ball pos=({ball_pos.x:.1f}, {ball_pos.y:.1f}), "
                  f"P2 score={self.game.player2_score}")
            
            if self.game.player2_score > initial_p2_score:
                print(f"SUCCESS: Player 2 scored on frame {frame + 1}!")
                scored = True
                break
        
        # Verify scoring occurred
        self.assertTrue(scored, "Player 2 should have scored when ball exited left side")
        self.assertEqual(self.game.player2_score, initial_p2_score + 1, 
                        "Player 2 score should have increased by 1")
    
    def test_scoring_when_ball_exits_right(self):
        """Test scoring when ball exits right side of screen."""
        # Get ball components
        ball_pos = self.game.entity_manager.get_component(self.game.ball, PositionComponent)
        ball_vel = self.game.entity_manager.get_component(self.game.ball, VelocityComponent)
        
        # Position ball near right boundary
        ball_pos.x = self.game.config.SCREEN_WIDTH - 15.0
        ball_pos.y = 300.0
        ball_vel.set_velocity(500.0, 0.0)  # Fast rightward velocity
        
        initial_p1_score = self.game.player1_score
        
        print(f"Initial ball position: ({ball_pos.x}, {ball_pos.y})")
        print(f"Initial Player 1 score: {initial_p1_score}")
        
        # Simulate several game updates
        scored = False
        for frame in range(10):
            dt = 1.0/60.0  # 60 FPS
            
            # Update movement system
            movement_entities = self.game.system_manager.get_entities_with_components(
                {PositionComponent, VelocityComponent})
            self.game.system_manager.get_system(MovementSystem).update(dt, movement_entities)
            
            # Update collision system
            collision_entities = self.game.system_manager.get_entities_with_components(
                {PositionComponent, CollisionComponent})
            self.game.system_manager.get_system(CollisionSystem).update(dt, collision_entities)
            
            # Check for scoring
            self.game._check_scoring()
            
            print(f"Frame {frame + 1}: Ball pos=({ball_pos.x:.1f}, {ball_pos.y:.1f}), "
                  f"P1 score={self.game.player1_score}")
            
            if self.game.player1_score > initial_p1_score:
                print(f"SUCCESS: Player 1 scored on frame {frame + 1}!")
                scored = True
                break
        
        # Verify scoring occurred
        self.assertTrue(scored, "Player 1 should have scored when ball exited right side")
        self.assertEqual(self.game.player1_score, initial_p1_score + 1, 
                        "Player 1 score should have increased by 1")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)