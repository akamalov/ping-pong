"""
Score system for handling game scoring logic and events.
"""

from typing import List, Set, Type, Optional, Callable
import time

from ..core.ecs import EntityID, System
from ..core.ecs.component import Component
from ..core.ecs.entity_manager import EntityManager
from ..components.score import ScoreComponent
from ..components.position import PositionComponent
from ..core.config import GameConfig


class ScoreSystem(System):
    """
    System that manages scoring logic and events.
    
    This system handles:
    - Detecting scoring conditions (ball off screen)
    - Updating score components
    - Triggering score events and callbacks
    - Managing game over conditions
    """
    
    def __init__(self, entity_manager: EntityManager, config: GameConfig):
        super().__init__()
        self.entity_manager = entity_manager
        self.config = config
        self.priority = 50  # Run after movement/collision but before render
        
        # Score-related entities
        self.score_manager_entity = None
        self.ball_entity = None
        
        # Event callbacks
        self.on_score_callbacks: List[Callable] = []
        self.on_game_over_callbacks: List[Callable] = []
        
        # Scoring detection settings
        self.score_boundary_left = -50  # Ball must be this far left to score for player 2
        self.score_boundary_right = config.SCREEN_WIDTH + 50  # Ball must be this far right to score for player 1
        
        # Timing for score events
        self.last_score_time = 0
        self.score_cooldown = 1.0  # Minimum time between scores (prevent double scoring)
    
    def get_required_components(self) -> Set[Type[Component]]:
        """Return the components required by this system."""
        return {ScoreComponent}
    
    def set_ball_entity(self, ball_entity: EntityID) -> None:
        """Set the ball entity to monitor for scoring."""
        self.ball_entity = ball_entity
    
    def set_score_manager_entity(self, score_entity: EntityID) -> None:
        """Set the score manager entity."""
        self.score_manager_entity = score_entity
    
    def add_score_callback(self, callback: Callable) -> None:
        """Add a callback function to be called when a player scores."""
        self.on_score_callbacks.append(callback)
    
    def add_game_over_callback(self, callback: Callable) -> None:
        """Add a callback function to be called when the game ends."""
        self.on_game_over_callbacks.append(callback)
    
    def update(self, dt: float, entities: List[EntityID]) -> None:
        """
        Update scoring logic.
        
        Args:
            dt: Delta time since last frame in seconds
            entities: List of entities with score components
        """
        # Check for scoring conditions if we have a ball
        if self.ball_entity and self.score_manager_entity:
            self._check_scoring_conditions()
        
        # Update score components
        for entity_id in entities:
            score_comp = self.entity_manager.get_component(entity_id, ScoreComponent)
            if score_comp:
                self._update_score_component(entity_id, score_comp, dt)
    
    def _check_scoring_conditions(self) -> None:
        """Check if scoring conditions are met."""
        current_time = time.time()
        
        # Respect score cooldown to prevent double scoring
        if current_time - self.last_score_time < self.score_cooldown:
            return
        
        # Get ball position
        ball_position = self.entity_manager.get_component(self.ball_entity, PositionComponent)
        if not ball_position:
            return
        
        # Get score component
        score_comp = self.entity_manager.get_component(self.score_manager_entity, ScoreComponent)
        if not score_comp or score_comp.game_over:
            return
        
        # Check for scoring
        scored = False
        scoring_player = None
        
        if ball_position.x < self.score_boundary_left:
            # Player 2 scores (ball went off left side)
            scoring_player = 2
            scored = True
        elif ball_position.x > self.score_boundary_right:
            # Player 1 scores (ball went off right side)  
            scoring_player = 1
            scored = True
        
        if scored and scoring_player:
            self._handle_score_event(scoring_player, score_comp)
            self.last_score_time = current_time
    
    def _handle_score_event(self, player: int, score_comp: ScoreComponent) -> None:
        """Handle a scoring event."""
        # Add the score
        game_over = score_comp.add_score(player, 1)
        
        # Create score event data
        score_event = {
            'player': player,
            'scores': score_comp.get_score_tuple(),
            'game_over': game_over,
            'winner': score_comp.winner if game_over else None
        }
        
        # Trigger score callbacks
        for callback in self.on_score_callbacks:
            try:
                callback(score_event)
            except Exception as e:
                print(f"Error in score callback: {e}")
        
        # Trigger game over callbacks if game ended
        if game_over:
            for callback in self.on_game_over_callbacks:
                try:
                    callback(score_event)
                except Exception as e:
                    print(f"Error in game over callback: {e}")
    
    def _update_score_component(self, entity_id: EntityID, score_comp: ScoreComponent, dt: float) -> None:
        """Update a score component."""
        # Update winning score from config if changed
        if score_comp.winning_score != self.config.WINNING_SCORE:
            score_comp.winning_score = self.config.WINNING_SCORE
    
    def reset_game(self) -> None:
        """Reset the game scores."""
        if self.score_manager_entity:
            score_comp = self.entity_manager.get_component(self.score_manager_entity, ScoreComponent)
            if score_comp:
                score_comp.reset_scores()
                self.last_score_time = 0
    
    def force_score(self, player: int, points: int = 1) -> bool:
        """
        Force add score for a player (for testing or special events).
        
        Args:
            player: Player number (1 or 2)
            points: Points to add
            
        Returns:
            True if this caused game over, False otherwise
        """
        if not self.score_manager_entity:
            return False
        
        score_comp = self.entity_manager.get_component(self.score_manager_entity, ScoreComponent)
        if not score_comp:
            return False
        
        game_over = score_comp.add_score(player, points)
        
        # Trigger callbacks
        score_event = {
            'player': player,
            'scores': score_comp.get_score_tuple(),
            'game_over': game_over,
            'winner': score_comp.winner if game_over else None,
            'forced': True
        }
        
        for callback in self.on_score_callbacks:
            try:
                callback(score_event)
            except Exception as e:
                print(f"Error in score callback: {e}")
        
        if game_over:
            for callback in self.on_game_over_callbacks:
                try:
                    callback(score_event)
                except Exception as e:
                        print(f"Error in game over callback: {e}")
        
        return game_over
    
    def get_current_scores(self) -> Optional[tuple]:
        """Get current scores as (player1_score, player2_score)."""
        if not self.score_manager_entity:
            return None
        
        score_comp = self.entity_manager.get_component(self.score_manager_entity, ScoreComponent)
        return score_comp.get_score_tuple() if score_comp else None
    
    def is_game_over(self) -> bool:
        """Check if the game is over."""
        if not self.score_manager_entity:
            return False
        
        score_comp = self.entity_manager.get_component(self.score_manager_entity, ScoreComponent)
        return score_comp.game_over if score_comp else False
    
    def get_winner(self) -> Optional[int]:
        """Get the winning player (None if game not over)."""
        if not self.score_manager_entity:
            return None
        
        score_comp = self.entity_manager.get_component(self.score_manager_entity, ScoreComponent)
        return score_comp.winner if score_comp and score_comp.game_over else None