"""
Integration test to verify that the complete scoring mechanism now works.
"""

import pytest
import pygame
from unittest.mock import Mock, patch
import sys
import os

# Add src to path so we can import the game modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ping_pong.core.game import Game
from ping_pong.core.config import GameConfig
from ping_pong.components.position import PositionComponent
from ping_pong.components.velocity import VelocityComponent
from ping_pong.components.collision import CollisionComponent, CollisionType
from ping_pong.systems.collision import CollisionSystem


class TestScoringIntegration:
    """Integration test for the complete scoring mechanism."""
    
    def test_complete_scoring_flow_now_works(self):
        """Test that the complete scoring flow now works end-to-end."""
        with patch('pygame.init'), patch('pygame.font.init'), patch('pygame.display.set_mode'):
            config = GameConfig()
            config.SCREEN_WIDTH = 800
            config.SCREEN_HEIGHT = 600
            config.WINNING_SCORE = 3
            
            # Create a minimal game instance
            game = Game.__new__(Game)
            game.config = config
            game.player1_score = 0
            game.player2_score = 0
            game.running = True
            game.paused = False
            
            # Create a real collision system (not mocked)
            from ping_pong.core.ecs.entity_manager import EntityManager
            entity_manager = EntityManager()
            collision_system = CollisionSystem(entity_manager, config)
            
            # Create a ball entity
            ball_entity = entity_manager.create_entity()
            
            # Test scenario 1: Ball goes off left side (Player 2 scores)
            print("Testing Player 2 scoring...")
            
            # Position ball off left side
            ball_position = PositionComponent(x=-20, y=300)
            ball_velocity = VelocityComponent(dx=-100, dy=0)
            ball_collision = CollisionComponent(
                width=10, height=10,
                collision_type=CollisionType.BALL,
                bounce_factor=1.0
            )
            
            entity_manager.add_component(ball_entity, ball_position)
            entity_manager.add_component(ball_entity, ball_velocity)
            entity_manager.add_component(ball_entity, ball_collision)
            
            # Process collision system - ball should stay off-screen
            collision_system._handle_boundary_collisions([ball_entity])
            
            # Ball should remain off-screen (not bounced back)
            assert ball_position.x < 0, "Ball should remain off left side for scoring"
            
            # Now test scoring detection
            game.ball = ball_entity
            game.entity_manager = entity_manager
            game.entity_factory = Mock()
            game.entity_factory.position_component_type = PositionComponent
            game._reset_ball = Mock()
            
            # Check scoring
            game._check_scoring()
            
            # Player 2 should have scored
            assert game.player2_score == 1, "Player 2 should have scored"
            assert game.player1_score == 0, "Player 1 should not have scored"
            game._reset_ball.assert_called_once()
            
            print("✅ Player 2 scoring works!")
            
            # Test scenario 2: Ball goes off right side (Player 1 scores)
            print("Testing Player 1 scoring...")
            
            # Reset for next test
            game._reset_ball.reset_mock()
            
            # Position ball off right side
            ball_position.x = config.SCREEN_WIDTH + 20
            ball_velocity.dx = 100  # Moving right
            
            # Process collision system - ball should stay off-screen
            collision_system._handle_boundary_collisions([ball_entity])
            
            # Ball should remain off-screen (not bounced back)
            assert ball_position.x > config.SCREEN_WIDTH, "Ball should remain off right side for scoring"
            
            # Check scoring
            game._check_scoring()
            
            # Player 1 should have scored
            assert game.player1_score == 1, "Player 1 should have scored"
            assert game.player2_score == 1, "Player 2 score should remain unchanged"
            game._reset_ball.assert_called_once()
            
            print("✅ Player 1 scoring works!")
            
            # Test scenario 3: Ball bounces off top/bottom (no scoring)
            print("Testing top/bottom bouncing (no scoring)...")
            
            # Reset for next test
            game._reset_ball.reset_mock()
            initial_p1_score = game.player1_score
            initial_p2_score = game.player2_score
            
            # Position ball off top
            ball_position.x = 400  # Middle of screen
            ball_position.y = -5   # Off top
            ball_velocity.dx = 50
            ball_velocity.dy = -100  # Moving up
            
            # Process collision system - ball should bounce back
            collision_system._handle_boundary_collisions([ball_entity])
            
            # Ball should be bounced back into bounds
            assert ball_position.y > 0, "Ball should be bounced back from top boundary"
            assert ball_velocity.dy > 0, "Ball velocity should be reflected downward"
            
            # Check scoring - should be no change
            game._check_scoring()
            
            assert game.player1_score == initial_p1_score, "No scoring should occur for top bounce"
            assert game.player2_score == initial_p2_score, "No scoring should occur for top bounce"
            game._reset_ball.assert_not_called()
            
            print("✅ Top/bottom bouncing works correctly!")
            
            print("🎉 Complete scoring mechanism is now working!")


if __name__ == "__main__":
    pytest.main([__file__])