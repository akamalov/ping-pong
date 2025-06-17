"""
Entity-Component-System (ECS) implementation.

This module provides a complete ECS architecture for the ping-pong game,
including entity management, component storage, and system execution.
"""

from typing import TypeVar, Type, NewType

# Core ECS Types
EntityID = NewType('EntityID', int)
ComponentType = TypeVar('ComponentType', bound='Component')

from .component import Component
from .system import System
from .entity_manager import EntityManager
from .component_manager import ComponentManager
from .system_manager import SystemManager

__all__ = [
    "EntityID",
    "ComponentType", 
    "Component",
    "System",
    "EntityManager",
    "ComponentManager",
    "SystemManager"
] 