"""
System Manager for the ECS system.

Manages system registration, execution order, and performance monitoring.
"""

from typing import List, Dict, Set, Type
import time

from . import EntityID
from .system import System
from .entity_manager import EntityManager
from .component import Component


class SystemManager:
    """
    Manages system registration and execution.
    
    The SystemManager is responsible for:
    - Registering and organizing systems
    - Executing systems in the correct order
    - Managing system dependencies and priorities
    - Performance monitoring and profiling
    """
    
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager
        self.systems: List[System] = []
        self.system_lookup: Dict[Type[System], System] = {}
        self.total_update_time = 0.0
        self.frame_count = 0
    
    def register_system(self, system: System) -> None:
        """
        Register a system for execution.
        
        Args:
            system: The system instance to register
        """
        if type(system) not in self.system_lookup:
            self.systems.append(system)
            self.system_lookup[type(system)] = system
            self._sort_systems_by_priority()
    
    def unregister_system(self, system_type: Type[System]) -> None:
        """
        Unregister a system from execution.
        
        Args:
            system_type: The type of system to unregister
        """
        if system_type in self.system_lookup:
            system = self.system_lookup[system_type]
            self.systems.remove(system)
            del self.system_lookup[system_type]
    
    def get_system(self, system_type: Type[System]) -> System:
        """
        Get a registered system by type.
        
        Args:
            system_type: The type of system to retrieve
            
        Returns:
            The system instance or None if not found
        """
        return self.system_lookup.get(system_type)
    
    def _sort_systems_by_priority(self) -> None:
        """Sort systems by their priority (lower values = higher priority)."""
        self.systems.sort(key=lambda s: s.priority)
    
    def update_all_systems(self, dt: float) -> None:
        """
        Update all registered systems.
        
        Args:
            dt: Delta time since last frame in seconds
        """
        frame_start_time = time.perf_counter()
        
        for system in self.systems:
            if not system.enabled:
                continue
            
            # Get entities that match this system's required components
            required_components = system.get_required_components()
            entities = self.entity_manager.get_entities_with_components(
                list(required_components)
            )
            
            # Update the system with profiling
            system.update_with_profiling(dt, entities)
        
        # Clean up destroyed entities at the end of the frame
        self.entity_manager.cleanup_destroyed_entities()
        
        # Update performance statistics
        frame_end_time = time.perf_counter()
        self.total_update_time += (frame_end_time - frame_start_time)
        self.frame_count += 1
    
    def enable_system(self, system_type: Type[System]) -> None:
        """Enable a system for execution."""
        system = self.get_system(system_type)
        if system:
            system.enabled = True
    
    def disable_system(self, system_type: Type[System]) -> None:
        """Disable a system from execution."""
        system = self.get_system(system_type)
        if system:
            system.enabled = False
    
    def set_system_priority(self, system_type: Type[System], priority: int) -> None:
        """
        Set the priority of a system.
        
        Args:
            system_type: The type of system to modify
            priority: New priority value (lower = higher priority)
        """
        system = self.get_system(system_type)
        if system:
            system.priority = priority
            self._sort_systems_by_priority()
    
    def get_performance_report(self) -> Dict[str, any]:
        """
        Get a comprehensive performance report for all systems.
        
        Returns:
            Dictionary containing performance statistics
        """
        report = {
            "total_systems": len(self.systems),
            "enabled_systems": len([s for s in self.systems if s.enabled]),
            "average_frame_time_ms": 0.0,
            "total_frames": self.frame_count,
            "systems": {}
        }
        
        if self.frame_count > 0:
            report["average_frame_time_ms"] = (
                self.total_update_time / self.frame_count
            ) * 1000
        
        # Get individual system performance
        for system in self.systems:
            system_name = type(system).__name__
            report["systems"][system_name] = system.get_performance_info()
        
        return report
    
    def reset_performance_stats(self) -> None:
        """Reset all performance statistics."""
        self.total_update_time = 0.0
        self.frame_count = 0
        
        for system in self.systems:
            system.performance_stats = system.performance_stats.__class__()
    
    def get_system_execution_order(self) -> List[str]:
        """Get the current system execution order."""
        return [type(system).__name__ for system in self.systems]
    
    def validate_system_dependencies(self) -> List[str]:
        """
        Validate system dependencies and return any issues.
        
        Returns:
            List of warning messages about potential dependency issues
        """
        warnings = []
        
        # Check for potential component conflicts
        component_writers: Dict[Type[Component], List[str]] = {}
        component_readers: Dict[Type[Component], List[str]] = {}
        
        for system in self.systems:
            system_name = type(system).__name__
            required_components = system.get_required_components()
            
            for component_type in required_components:
                # Assume all systems both read and potentially write components
                # In a more sophisticated system, we'd have separate read/write declarations
                if component_type not in component_writers:
                    component_writers[component_type] = []
                    component_readers[component_type] = []
                
                component_writers[component_type].append(system_name)
                component_readers[component_type].append(system_name)
        
        # Check for potential race conditions (multiple writers)
        for component_type, writers in component_writers.items():
            if len(writers) > 1:
                warnings.append(
                    f"Component {component_type.__name__} is modified by multiple systems: "
                    f"{', '.join(writers)}. Consider execution order."
                )
        
        return warnings 