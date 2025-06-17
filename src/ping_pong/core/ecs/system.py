"""
Base System class for the ECS system.

Systems contain the logic and behavior that operates on components.
They process entities that have specific component combinations.
"""

from abc import ABC, abstractmethod
from typing import List, Set, Type, Dict
from collections import defaultdict, deque
import time

from . import EntityID, ComponentType
from .component import Component


class PerformanceStats:
    """Performance statistics tracking for systems."""
    
    def __init__(self, max_samples: int = 60):
        self.update_times: deque = deque(maxlen=max_samples)
        self.entity_counts: deque = deque(maxlen=max_samples)
        self.max_samples = max_samples
    
    def record_update(self, update_time: float, entity_count: int) -> None:
        """Record performance data for an update cycle."""
        self.update_times.append(update_time)
        self.entity_counts.append(entity_count)
    
    def get_average_update_time(self) -> float:
        """Get average update time in milliseconds."""
        if not self.update_times:
            return 0.0
        return sum(self.update_times) / len(self.update_times) * 1000
    
    def get_average_entity_count(self) -> float:
        """Get average number of entities processed."""
        if not self.entity_counts:
            return 0.0
        return sum(self.entity_counts) / len(self.entity_counts)


class System(ABC):
    """
    Base class for all ECS systems.
    
    Systems contain the logic that operates on entities with specific
    component combinations. They are responsible for updating game state
    and implementing game behaviors.
    """
    
    def __init__(self):
        self.performance_stats = PerformanceStats()
        self.enabled = True
        self.priority = 0  # Lower values = higher priority
    
    @abstractmethod
    def update(self, dt: float, entities: List[EntityID]) -> None:
        """
        Update the system for the current frame.
        
        Args:
            dt: Delta time since last frame in seconds
            entities: List of entities that match required components
        """
        pass
    
    @abstractmethod
    def get_required_components(self) -> Set[Type[Component]]:
        """
        Get the component types required by this system.
        
        Returns:
            Set of component types that entities must have to be processed
        """
        pass
    
    def update_with_profiling(self, dt: float, entities: List[EntityID]) -> None:
        """Update the system with performance profiling."""
        if not self.enabled:
            return
            
        start_time = time.perf_counter()
        self.update(dt, entities)
        end_time = time.perf_counter()
        
        self.performance_stats.record_update(
            end_time - start_time,
            len(entities)
        )
    
    def get_performance_info(self) -> Dict[str, float]:
        """Get performance information for this system."""
        return {
            "average_update_time_ms": self.performance_stats.get_average_update_time(),
            "average_entity_count": self.performance_stats.get_average_entity_count(),
            "enabled": self.enabled,
            "priority": self.priority
        } 