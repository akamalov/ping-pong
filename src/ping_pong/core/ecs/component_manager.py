"""
Component Manager for advanced component operations.

Provides additional functionality for component management,
including component pools and serialization.
"""

from typing import Dict, Type, List, Any, Optional
from collections import defaultdict

from . import EntityID
from .component import Component


class ComponentPool:
    """Object pool for component instances to reduce garbage collection."""
    
    def __init__(self, component_type: Type[Component], initial_size: int = 10):
        self.component_type = component_type
        self.available: List[Component] = []
        self.in_use: set = set()
        self._expand_pool(initial_size)
    
    def _expand_pool(self, size: int) -> None:
        """Expand the pool with new component instances."""
        for _ in range(size):
            # Create default instance (components must support default construction)
            try:
                component = self.component_type()
                self.available.append(component)
            except TypeError:
                # Component doesn't support default construction
                break
    
    def acquire(self) -> Optional[Component]:
        """Get a component instance from the pool."""
        if not self.available:
            self._expand_pool(10)
        
        if self.available:
            component = self.available.pop()
            self.in_use.add(id(component))
            return component
        
        return None
    
    def release(self, component: Component) -> None:
        """Return a component instance to the pool."""
        component_id = id(component)
        if component_id in self.in_use:
            self.in_use.remove(component_id)
            # Reset component to default state if possible
            self._reset_component(component)
            self.available.append(component)
    
    def _reset_component(self, component: Component) -> None:
        """Reset component to default state."""
        # This is a basic implementation - components can override this
        # by implementing a reset() method
        if hasattr(component, 'reset'):
            component.reset()


class ComponentManager:
    """
    Advanced component management with pooling and serialization.
    
    Provides additional functionality beyond the basic EntityManager,
    including component object pooling for performance and component
    serialization for save/load functionality.
    """
    
    def __init__(self):
        self._component_pools: Dict[Type[Component], ComponentPool] = {}
        self._component_registry: Dict[str, Type[Component]] = {}
    
    def register_component_type(self, component_type: Type[Component]) -> None:
        """
        Register a component type for pooling and serialization.
        
        Args:
            component_type: The component class to register
        """
        self._component_registry[component_type.__name__] = component_type
        
        # Create object pool for this component type
        if component_type not in self._component_pools:
            self._component_pools[component_type] = ComponentPool(component_type)
    
    def create_component(self, component_type: Type[Component], **kwargs) -> Component:
        """
        Create a component instance, using object pool if available.
        
        Args:
            component_type: The type of component to create
            **kwargs: Component initialization parameters
            
        Returns:
            A component instance
        """
        # Try to get from pool first
        if component_type in self._component_pools:
            component = self._component_pools[component_type].acquire()
            if component is not None:
                # Update component with provided parameters
                for key, value in kwargs.items():
                    if hasattr(component, key):
                        setattr(component, key, value)
                return component
        
        # Create new instance if pool is not available or empty
        return component_type(**kwargs)
    
    def release_component(self, component: Component) -> None:
        """
        Release a component back to the object pool.
        
        Args:
            component: The component to release
        """
        component_type = type(component)
        if component_type in self._component_pools:
            self._component_pools[component_type].release(component)
    
    def serialize_components(self, components: Dict[Type[Component], Component]) -> Dict[str, Any]:
        """
        Serialize a collection of components to JSON-serializable format.
        
        Args:
            components: Dictionary mapping component types to instances
            
        Returns:
            Dictionary suitable for JSON serialization
        """
        serialized = {}
        for component_type, component in components.items():
            component_name = component_type.__name__
            try:
                # Use dataclass_json serialization if available
                if hasattr(component, 'to_dict'):
                    serialized[component_name] = component.to_dict()
                else:
                    # Fallback to basic dict conversion
                    serialized[component_name] = component.__dict__.copy()
            except Exception as e:
                print(f"Warning: Could not serialize component {component_name}: {e}")
        
        return serialized
    
    def deserialize_components(self, serialized_data: Dict[str, Any]) -> Dict[Type[Component], Component]:
        """
        Deserialize components from JSON data.
        
        Args:
            serialized_data: Dictionary containing serialized component data
            
        Returns:
            Dictionary mapping component types to deserialized instances
        """
        components = {}
        
        for component_name, component_data in serialized_data.items():
            if component_name in self._component_registry:
                component_type = self._component_registry[component_name]
                try:
                    # Use dataclass_json deserialization if available
                    if hasattr(component_type, 'from_dict'):
                        component = component_type.from_dict(component_data)
                    else:
                        # Fallback to basic construction
                        component = component_type(**component_data)
                    
                    components[component_type] = component
                except Exception as e:
                    print(f"Warning: Could not deserialize component {component_name}: {e}")
        
        return components
    
    def get_registered_component_types(self) -> List[Type[Component]]:
        """Get all registered component types."""
        return list(self._component_registry.values())
    
    def get_pool_stats(self) -> Dict[str, Dict[str, int]]:
        """Get statistics about component pools."""
        stats = {}
        for component_type, pool in self._component_pools.items():
            stats[component_type.__name__] = {
                "available": len(pool.available),
                "in_use": len(pool.in_use),
                "total": len(pool.available) + len(pool.in_use)
            }
        return stats 