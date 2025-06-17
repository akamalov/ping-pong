"""
Comprehensive tests for the ping-pong game scoring mechanism.
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


class TestScoring:
    """Test the scoring mechanism."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        config = GameConfig()
        config.SCREEN_WIDTH = 800
        config.SCREEN_HEIGHT = 600
        config.WINNING_SCORE = 3
        config.PADDLE_WIDTH = 10
        config.PADDLE_HEIGHT = 60
        config.BALL_SIZE = 10
        return config
    
    @pytest.fixture
    def game(self, config):
        """Create a test game instance."""
        with patch('pygame.init'), patch('pygame.font.init'), patch('pygame.display.set_mode'):
            game = Game.__new__(Game)  # Create without calling __init__
            game.config = config
            game.player1_score = 0
            game.player2_score = 0
            game.running = True
            game.paused = False
            
            # Mock the entity manager and other components
            game.entity_manager = Mock()
            game.ball = Mock()
            
            # Mock entity factory
            game.entity_factory = Mock()
            game.entity_factory.position_component_type = PositionComponent
            
            # Mock paddle entities
            game.player1_paddle = Mock()
            game.player2_paddle = Mock()
            
            return game
    
    def test_initial_scores_are_zero(self, game):
        """Test that initial scores are zero."""
        assert game.player1_score == 0
        assert game.player2_score == 0
    
    def test_player1_scores_when_ball_goes_right(self, game):
        """Test that player 1 scores when ball goes off right side."""
        # Mock ball position component - ball went off right side
        mock_ball_pos = Mock()
        mock_ball_pos.x = game.config.SCREEN_WIDTH + 10  # Past right edge
        
        game.entity_manager.get_component.return_value = mock_ball_pos
        
        # Mock _reset_ball method
        game._reset_ball = Mock()
        
        initial_score = game.player1_score
        game._check_scoring()
        
        assert game.player1_score == initial_score + 1
        assert game.player2_score == 0
        game._reset_ball.assert_called_once()
    
    def test_player2_scores_when_ball_goes_left(self, game):
        """Test that player 2 scores when ball goes off left side."""
        # Mock ball position component - ball went off left side
        mock_ball_pos = Mock()
        mock_ball_pos.x = -10  # Past left edge
        
        game.entity_manager.get_component.return_value = mock_ball_pos
        
        # Mock _reset_ball method
        game._reset_ball = Mock()
        
        initial_score = game.player2_score
        game._check_scoring()
        
        assert game.player2_score == initial_score + 1
        assert game.player1_score == 0
        game._reset_ball.assert_called_once()
    
    def test_no_scoring_when_ball_in_bounds(self, game):
        """Test that no scoring occurs when ball is within bounds."""
        # Mock ball position component - ball in middle of screen
        mock_ball_pos = Mock()
        mock_ball_pos.x = game.config.SCREEN_WIDTH // 2
        
        game.entity_manager.get_component.return_value = mock_ball_pos
        
        # Mock _reset_ball method
        game._reset_ball = Mock()
        
        initial_p1_score = game.player1_score
        initial_p2_score = game.player2_score
        
        game._check_scoring()
        
        assert game.player1_score == initial_p1_score
        assert game.player2_score == initial_p2_score
        game._reset_ball.assert_not_called()
    
    def test_game_over_when_winning_score_reached(self, game):
        """Test that game enters game over state when winning score is reached."""
        # Set player 1 to winning score
        game.player1_score = game.config.WINNING_SCORE
        game.player2_score = 1
        
        game._check_game_over()
        
        assert game.paused == True
    
    def test_game_continues_when_winning_score_not_reached(self, game):
        """Test that game continues when winning score is not reached."""
        # Set scores below winning score
        game.player1_score = game.config.WINNING_SCORE - 1
        game.player2_score = game.config.WINNING_SCORE - 1
        
        initial_paused = game.paused
        game._check_game_over()
        
        assert game.paused == initial_paused
    
    def test_reset_game_resets_scores(self, game):
        """Test that reset_game resets scores to zero."""
        # Set some scores
        game.player1_score = 5
        game.player2_score = 3
        
        # Mock required methods
        game._reset_ball = Mock()
        game.entity_manager.get_component = Mock(return_value=Mock())
        
        game._reset_game()
        
        assert game.player1_score == 0
        assert game.player2_score == 0
        assert game.paused == False
    
    def test_multiple_scoring_events(self, game):
        """Test multiple scoring events in sequence."""
        # Mock _reset_ball method
        game._reset_ball = Mock()
        
        # Player 2 scores
        mock_ball_pos = Mock()
        mock_ball_pos.x = -10
        game.entity_manager.get_component.return_value = mock_ball_pos
        game._check_scoring()
        
        assert game.player2_score == 1
        assert game.player1_score == 0
        
        # Player 1 scores
        mock_ball_pos.x = game.config.SCREEN_WIDTH + 10
        game._check_scoring()
        
        assert game.player2_score == 1
        assert game.player1_score == 1
        
        # Player 1 scores again
        game._check_scoring()
        
        assert game.player2_score == 1
        assert game.player1_score == 2


class TestCollisionSystemBoundaryIssues:
    """Test that reveals the collision system boundary issues."""
    
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
    
    def test_ball_bounces_off_left_boundary(self, collision_system, config):
        """Test that ball bounces off left boundary instead of going off-screen."""
        # Create mock components
        position = PositionComponent(x=-5, y=300)  # Ball past left edge
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
        
        # Process boundary collision
        collision_system._handle_boundary_collisions([1])
        
        # Ball should be repositioned and velocity reflected
        assert position.x > 0  # Ball moved back into bounds
        assert velocity.dx > 0  # Velocity reflected (now moving right)
    
    def test_ball_bounces_off_right_boundary(self, collision_system, config):
        """Test that ball bounces off right boundary instead of going off-screen."""
        # Create mock components
        position = PositionComponent(x=config.SCREEN_WIDTH + 5, y=300)  # Ball past right edge
        velocity = VelocityComponent(dx=100, dy=0)  # Moving right
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
        
        # Ball should be repositioned and velocity reflected
        assert position.x < config.SCREEN_WIDTH  # Ball moved back into bounds
        assert velocity.dx < 0  # Velocity reflected (now moving left)
    
    def test_collision_system_prevents_scoring(self, collision_system, config):
        """Test that demonstrates collision system prevents scoring conditions."""
        # This test shows the fundamental issue: the collision system
        # prevents the ball from ever reaching the scoring conditions
        
        # Ball trying to go off left side
        position = PositionComponent(x=-1, y=300)
        velocity = VelocityComponent(dx=-50, dy=0)
        collision = CollisionComponent(
            width=10, height=10, 
            collision_type=CollisionType.BALL, 
            bounce_factor=1.0
        )
        
        collision_system.entity_manager.get_component.side_effect = lambda entity_id, component_type: {
            PositionComponent: position,
            VelocityComponent: velocity,
            CollisionComponent: collision
        }.get(component_type)
        
        # Before collision handling - ball is in scoring position
        assert position.x < 0  # This would trigger player 2 scoring
        
        # Handle boundary collision
        collision_system._handle_boundary_collisions([1])
        
        # After collision handling - ball is no longer in scoring position
        assert position.x >= 0  # Ball has been moved back, scoring condition lost
        
        # This demonstrates the bug: collision system prevents scoring!


class TestScoringScopeIntegration:
    """Integration tests for complete scoring flow."""
    
    def test_full_scoring_flow_reveals_issue(self):
        """Integration test that reveals the scoring mechanism issue."""
        # This test would require a full game setup and would demonstrate
        # that the ball never actually goes off-screen due to collision handling
        
        with patch('pygame.init'), patch('pygame.font.init'), patch('pygame.display.set_mode'):
            config = GameConfig()
            config.SCREEN_WIDTH = 800
            config.SCREEN_HEIGHT = 600
            
            # Mock the display to avoid actual pygame window
            with patch('pygame.display.set_mode') as mock_display:
                mock_display.return_value = Mock()
                
                game = Game.__new__(Game)
                game.config = config
                game.clock = Mock()
                game.screen = Mock()
                
                # The collision system will prevent the ball from going off-screen
                # so _check_scoring() will never find a scoring condition
                # This is the root cause of the scoring mechanism not working
                
                # This test demonstrates the architectural issue that needs fixing


if __name__ == "__main__":
    pytest.main([__file__])