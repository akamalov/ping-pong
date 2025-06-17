"""
Input component for handling user input.
"""

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Dict, Set
import pygame

from ..core.ecs.component import Component


@dataclass_json
@dataclass
class InputComponent(Component):
    """
    Component that handles input mapping and state for an entity.
    
    Attributes:
        key_bindings: Dictionary mapping action names to pygame key codes
        enabled: Whether input is currently enabled
        move_speed: Speed multiplier for movement actions
    """
    key_bindings: Dict[str, int] = field(default_factory=dict)
    enabled: bool = True
    move_speed: float = 300.0  # pixels per second
    
    # Runtime state (not serialized)
    current_actions: Set[str] = field(default_factory=set, init=False)
    previous_actions: Set[str] = field(default_factory=set, init=False)
    
    def reset(self) -> None:
        """Reset to default input state."""
        self.key_bindings.clear()
        self.enabled = True
        self.move_speed = 300.0
        self.current_actions.clear()
        self.previous_actions.clear()
    
    def bind_key(self, action: str, key_code: int) -> None:
        """Bind an action to a key code."""
        self.key_bindings[action] = key_code
    
    def unbind_key(self, action: str) -> None:
        """Remove a key binding."""
        if action in self.key_bindings:
            del self.key_bindings[action]
    
    def get_key_for_action(self, action: str) -> int:
        """Get the key code for an action."""
        return self.key_bindings.get(action, -1)
    
    def is_action_active(self, action: str) -> bool:
        """Check if an action is currently active."""
        return action in self.current_actions
    
    def is_action_just_pressed(self, action: str) -> bool:
        """Check if an action was just pressed this frame."""
        return (action in self.current_actions and 
                action not in self.previous_actions)
    
    def is_action_just_released(self, action: str) -> bool:
        """Check if an action was just released this frame."""
        return (action not in self.current_actions and 
                action in self.previous_actions)
    
    def update_input_state(self, pressed_keys: Set[int]) -> None:
        """Update the input state based on currently pressed keys."""
        if not self.enabled:
            self.current_actions.clear()
            return
        
        # Store previous state
        self.previous_actions = self.current_actions.copy()
        self.current_actions.clear()
        
        # Check which actions are currently active
        for action, key_code in self.key_bindings.items():
            if key_code in pressed_keys:
                self.current_actions.add(action)
    
    def get_movement_vector(self) -> tuple:
        """
        Get the movement vector based on current input.
        
        Returns:
            Tuple of (dx, dy) representing movement direction
        """
        dx, dy = 0.0, 0.0
        
        if self.is_action_active("move_up"):
            dy -= 1.0
        if self.is_action_active("move_down"):
            dy += 1.0
        if self.is_action_active("move_left"):
            dx -= 1.0
        if self.is_action_active("move_right"):
            dx += 1.0
        
        return dx, dy
    
    def get_movement_velocity(self) -> tuple:
        """
        Get the movement velocity based on current input and move speed.
        
        Returns:
            Tuple of (vx, vy) in pixels per second
        """
        dx, dy = self.get_movement_vector()
        return dx * self.move_speed, dy * self.move_speed
    
    def setup_default_bindings(self, player_number: int = 1) -> None:
        """
        Set up default key bindings for a player.
        
        Args:
            player_number: Player number (1 or 2) for different key sets
        """
        if player_number == 1:
            # Player 1: WASD keys
            self.bind_key("move_up", pygame.K_w)
            self.bind_key("move_down", pygame.K_s)
            self.bind_key("move_left", pygame.K_a)
            self.bind_key("move_right", pygame.K_d)
        elif player_number == 2:
            # Player 2: Arrow keys
            self.bind_key("move_up", pygame.K_UP)
            self.bind_key("move_down", pygame.K_DOWN)
            self.bind_key("move_left", pygame.K_LEFT)
            self.bind_key("move_right", pygame.K_RIGHT)
    
    def __str__(self) -> str:
        active_actions = ", ".join(self.current_actions) if self.current_actions else "none"
        return (f"Input(enabled: {self.enabled}, "
                f"bindings: {len(self.key_bindings)}, "
                f"active: [{active_actions}])") 