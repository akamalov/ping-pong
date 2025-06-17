"""
Movement system for updating entity positions based on velocity.
"""

from typing import List, Set, Type

from ..core.ecs import EntityID, System
from ..core.ecs.component import Component
from ..components.position import PositionComponent
from ..components.velocity import VelocityComponent
from ..core.ecs.entity_manager import EntityManager


class MovementSystem(System):
    """
    System that updates entity positions based on their velocity.
    
    This system processes all entities that have both PositionComponent
    and VelocityComponent, updating their positions each frame based on
    their velocity and the frame delta time.
    """
    
    def __init__(self, entity_manager: EntityManager):
        super().__init__()
        self.entity_manager = entity_manager
        self.priority = 10  # Early in the update cycle
    
    def get_required_components(self) -> Set[Type[Component]]:
        """Return the components required by this system."""
        return {PositionComponent, VelocityComponent}
    
    def update(self, dt: float, entities: List[EntityID]) -> None:
        """
        Update positions based on velocity.
        
        Args:
            dt: Delta time since last frame in seconds
            entities: List of entities with required components
        """
        for entity_id in entities:
            position = self.entity_manager.get_component(entity_id, PositionComponent)
            velocity = self.entity_manager.get_component(entity_id, VelocityComponent)
            
            if position and velocity:
                # Update position based on velocity and delta time
                position.x += velocity.dx * dt
                position.y += velocity.dy * dt 