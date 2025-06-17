"""
Entity Manager for the ECS system.

Manages entity lifecycle, component assignment, and entity queries.
"""

from typing import Dict, List, Set, Type, Optional, Iterator
from collections import defaultdict

from . import EntityID, ComponentType
from .component import Component


class EntityManager:
    """
    Manages entity lifecycle and component assignments.
    
    The EntityManager is responsible for:
    - Creating and destroying entities
    - Adding and removing components from entities
    - Querying entities by component types
    - Managing entity-component relationships
    """
    
    def __init__(self):
        self._next_entity_id: int = 1
        self._entities: Set[EntityID] = set()
        self._components: Dict[EntityID, Dict[Type[Component], Component]] = defaultdict(dict)
        self._component_to_entities: Dict[Type[Component], Set[EntityID]] = defaultdict(set)
        self._entities_to_destroy: Set[EntityID] = set()
    
    def create_entity(self) -> EntityID:
        """
        Create a new entity.
        
        Returns:
            The ID of the newly created entity
        """
        entity_id = EntityID(self._next_entity_id)
        self._next_entity_id += 1
        self._entities.add(entity_id)
        return entity_id
    
    def destroy_entity(self, entity_id: EntityID) -> None:
        """
        Mark an entity for destruction.
        
        The entity will be destroyed at the end of the current frame
        to avoid issues with systems currently processing it.
        
        Args:
            entity_id: The entity to destroy
        """
        if entity_id in self._entities:
            self._entities_to_destroy.add(entity_id)
    
    def add_component(self, entity_id: EntityID, component: Component) -> None:
        """
        Add a component to an entity.
        
        Args:
            entity_id: The entity to add the component to
            component: The component instance to add
        """
        if entity_id not in self._entities:
            raise ValueError(f"Entity {entity_id} does not exist")
        
        component_type = type(component)
        self._components[entity_id][component_type] = component
        self._component_to_entities[component_type].add(entity_id)
    
    def remove_component(self, entity_id: EntityID, component_type: Type[Component]) -> None:
        """
        Remove a component from an entity.
        
        Args:
            entity_id: The entity to remove the component from
            component_type: The type of component to remove
        """
        if entity_id not in self._entities:
            return
        
        if component_type in self._components[entity_id]:
            del self._components[entity_id][component_type]
            self._component_to_entities[component_type].discard(entity_id)
    
    def get_component(self, entity_id: EntityID, component_type: Type[ComponentType]) -> Optional[ComponentType]:
        """
        Get a component from an entity.
        
        Args:
            entity_id: The entity to get the component from
            component_type: The type of component to retrieve
            
        Returns:
            The component instance or None if not found
        """
        if entity_id not in self._entities:
            return None
        
        return self._components[entity_id].get(component_type)
    
    def has_component(self, entity_id: EntityID, component_type: Type[Component]) -> bool:
        """
        Check if an entity has a specific component.
        
        Args:
            entity_id: The entity to check
            component_type: The type of component to check for
            
        Returns:
            True if the entity has the component, False otherwise
        """
        if entity_id not in self._entities:
            return False
        
        return component_type in self._components[entity_id]
    
    def get_entities_with_components(self, component_types: List[Type[Component]]) -> List[EntityID]:
        """
        Get all entities that have all of the specified components.
        
        Args:
            component_types: List of component types that entities must have
            
        Returns:
            List of entity IDs that have all specified components
        """
        if not component_types:
            return list(self._entities)
        
        # Start with entities that have the first component type
        result_entities = self._component_to_entities[component_types[0]].copy()
        
        # Intersect with entities that have each additional component type
        for component_type in component_types[1:]:
            result_entities &= self._component_to_entities[component_type]
        
        # Filter out entities marked for destruction
        return [entity_id for entity_id in result_entities 
                if entity_id not in self._entities_to_destroy]
    
    def get_all_entities(self) -> List[EntityID]:
        """
        Get all active entities.
        
        Returns:
            List of all entity IDs (excluding those marked for destruction)
        """
        return [entity_id for entity_id in self._entities 
                if entity_id not in self._entities_to_destroy]
    
    def cleanup_destroyed_entities(self) -> None:
        """
        Remove all entities marked for destruction.
        
        This should be called at the end of each frame.
        """
        for entity_id in self._entities_to_destroy:
            # Remove all components from the entity
            if entity_id in self._components:
                for component_type in list(self._components[entity_id].keys()):
                    self.remove_component(entity_id, component_type)
                del self._components[entity_id]
            
            # Remove from entities set
            self._entities.discard(entity_id)
        
        self._entities_to_destroy.clear()
    
    def get_entity_count(self) -> int:
        """Get the number of active entities."""
        return len(self._entities) - len(self._entities_to_destroy)
    
    def get_component_count(self, component_type: Type[Component]) -> int:
        """Get the number of entities with a specific component type."""
        return len(self._component_to_entities[component_type])
    
    def clear_all(self) -> None:
        """Remove all entities and components."""
        self._entities.clear()
        self._components.clear()
        self._component_to_entities.clear()
        self._entities_to_destroy.clear()
        self._next_entity_id = 1 