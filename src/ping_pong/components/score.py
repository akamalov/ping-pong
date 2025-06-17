"""
Score component for managing game scoring.
"""

from typing import Dict, Any, Optional
from ..core.ecs.component import Component


class ScoreComponent(Component):
    """
    Component that manages score data for players.
    
    This component can be attached to a score manager entity or individual
    player entities to track scoring information.
    """
    
    def __init__(self, player1_score: int = 0, player2_score: int = 0,
                 winning_score: int = 10, score_to_win: bool = True):
        """
        Initialize score component.
        
        Args:
            player1_score: Initial score for player 1
            player2_score: Initial score for player 2  
            winning_score: Score needed to win the game
            score_to_win: Whether the game should end when winning score is reached
        """
        super().__init__()
        self.player1_score = player1_score
        self.player2_score = player2_score
        self.winning_score = winning_score
        self.score_to_win = score_to_win
        
        # Game state tracking
        self.game_over = False
        self.winner = None  # 1 or 2 for player 1 or 2
        
        # Event tracking
        self.last_scorer = None  # Track who scored last
        self.score_events = []  # List of recent scoring events
        self.max_events = 10  # Maximum score events to track
    
    def add_score(self, player: int, points: int = 1) -> bool:
        """
        Add points to a player's score.
        
        Args:
            player: Player number (1 or 2)
            points: Number of points to add
            
        Returns:
            True if this scoring caused the game to end, False otherwise
        """
        if self.game_over:
            return False
        
        if player == 1:
            self.player1_score += points
        elif player == 2:
            self.player2_score += points
        else:
            return False
        
        # Track scoring event
        self.last_scorer = player
        self._add_score_event(player, points)
        
        # Check for game over
        if self.score_to_win:
            if self.player1_score >= self.winning_score:
                self.game_over = True
                self.winner = 1
                return True
            elif self.player2_score >= self.winning_score:
                self.game_over = True
                self.winner = 2
                return True
        
        return False
    
    def reset_scores(self, reset_game_state: bool = True) -> None:
        """
        Reset all scores to zero.
        
        Args:
            reset_game_state: Whether to also reset game over state
        """
        self.player1_score = 0
        self.player2_score = 0
        self.last_scorer = None
        self.score_events.clear()
        
        if reset_game_state:
            self.game_over = False
            self.winner = None
    
    def get_score_difference(self) -> int:
        """Get the score difference (positive means player 1 is ahead)."""
        return self.player1_score - self.player2_score
    
    def get_leading_player(self) -> Optional[int]:
        """Get the player who is currently leading (None if tied)."""
        if self.player1_score > self.player2_score:
            return 1
        elif self.player2_score > self.player1_score:
            return 2
        return None
    
    def is_tied(self) -> bool:
        """Check if the scores are tied."""
        return self.player1_score == self.player2_score
    
    def get_score_tuple(self) -> tuple:
        """Get scores as a tuple (player1_score, player2_score)."""
        return (self.player1_score, self.player2_score)
    
    def _add_score_event(self, player: int, points: int) -> None:
        """Add a scoring event to the event history."""
        event = {
            'player': player,
            'points': points,
            'timestamp': None,  # Could add actual timestamp if needed
            'scores_after': self.get_score_tuple()
        }
        
        self.score_events.append(event)
        
        # Keep only the most recent events
        if len(self.score_events) > self.max_events:
            self.score_events.pop(0)
    
    def get_recent_events(self, count: int = 5) -> list:
        """Get the most recent scoring events."""
        return self.score_events[-count:] if self.score_events else []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary representation."""
        return {
            'player1_score': self.player1_score,
            'player2_score': self.player2_score,
            'winning_score': self.winning_score,
            'score_to_win': self.score_to_win,
            'game_over': self.game_over,
            'winner': self.winner,
            'last_scorer': self.last_scorer,
            'recent_events': self.get_recent_events()
        }
    
    def __str__(self) -> str:
        """String representation of the score."""
        status = ""
        if self.game_over:
            status = f" (Game Over - Player {self.winner} wins!)"
        return f"Score: {self.player1_score} - {self.player2_score}{status}"