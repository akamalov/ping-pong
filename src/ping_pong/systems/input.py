"""
Input system for handling player input.
"""

from typing import List, Set, Type
import pygame

from ..core.ecs import EntityID, System
from ..core.ecs.component import Component
from ..components.input import InputComponent
from ..components.velocity import VelocityComponent
from ..core.ecs.entity_manager import EntityManager


class InputSystem(System):
    """
    System that handles input processing for entities.
    
    This system processes all entities with input components,
    reads the current input state, and updates their velocity
    or other components based on input actions.
    """
    
    def __init__(self, entity_manager: EntityManager):
        super().__init__()
        self.entity_manager = entity_manager
        self.priority = 5  # Very early in the update cycle
        
        # Track current input state
        self.current_keys: Set[int] = set()
    
    def get_required_components(self) -> Set[Type[Component]]:
        """Return the components required by this system."""
        return {InputComponent}
    
    def update(self, dt: float, entities: List[EntityID]) -> None:
        """
        Update input processing.
        
        Args:
            dt: Delta time since last frame in seconds
            entities: List of entities with required components
        """
        # Get current input state from pygame
        self._update_input_state()
        
        # Process input for each entity
        for entity_id in entities:
            input_comp = self.entity_manager.get_component(entity_id, InputComponent)
            velocity_comp = self.entity_manager.get_component(entity_id, VelocityComponent)
            
            if input_comp:
                # Update input component state
                input_comp.update_input_state(self.current_keys)
                
                # Apply input to velocity if entity has velocity component
                if velocity_comp:
                    self._apply_input_to_velocity(input_comp, velocity_comp)
    
    def _update_input_state(self) -> None:
        """Update the current input state from pygame."""
        # Get currently pressed keys
        pressed_keys = pygame.key.get_pressed()
        
        # Convert to set of key codes
        self.current_keys.clear()
        for key_code in range(len(pressed_keys)):
            if pressed_keys[key_code]:
                self.current_keys.add(key_code)
    
    def _apply_input_to_velocity(self, input_comp: InputComponent, velocity_comp: VelocityComponent) -> None:
        """Apply input actions to velocity component."""
        if not input_comp.enabled:
            return
        
        # Get movement velocity from input
        vx, vy = input_comp.get_movement_velocity()
        
        # Set velocity based on input
        velocity_comp.set_velocity(vx, vy)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle a pygame event.
        
        Args:
            event: The pygame event to handle
            
        Returns:
            True if the event was handled, False otherwise
        """
        # This can be used for discrete input events like key presses
        # For now, we handle continuous input in the update method
        return False 