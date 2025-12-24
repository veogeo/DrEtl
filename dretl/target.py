"""
Base Target class for WRITE-ONLY data loading.

Targets are responsible for consuming a RewritePlan and loading
data into the target backend/format.
"""

from abc import ABC, abstractmethod
from typing import Optional
from dretl.models import RewritePlan


class Target(ABC):
    """
    Abstract base class for data targets.
    
    Targets are WRITE-ONLY loaders that consume a RewritePlan
    and write data to a target backend.
    """
    
    @classmethod
    @abstractmethod
    def get_target_type(cls) -> str:
        """
        Get the target type identifier for this target.
        
        Returns:
            Target type string (e.g., "postgis", "gpkg", "geojson")
        """
        pass
    
    @abstractmethod
    def load(self, plan: RewritePlan, **kwargs) -> dict:
        """
        Execute a rewrite plan and load data to the target.
        
        Args:
            plan: RewritePlan describing the data transformation
            **kwargs: Additional target-specific options
            
        Returns:
            Dictionary with execution results (layers written, errors, etc.)
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type={self.get_target_type()})"


class TargetRegistry:
    """Registry for managing available targets."""
    
    _targets = {}
    
    @classmethod
    def register(cls, target_class: type) -> None:
        """
        Register a target class.
        
        Args:
            target_class: Target class to register
        """
        if not issubclass(target_class, Target):
            raise ValueError(f"{target_class} must be a subclass of Target")
        target_type = target_class.get_target_type()
        cls._targets[target_type] = target_class
    
    @classmethod
    def get_target(cls, target_type: str) -> Optional[Target]:
        """
        Get a target instance by type.
        
        Args:
            target_type: Target type identifier
            
        Returns:
            Target instance if found, None otherwise
        """
        target_class = cls._targets.get(target_type)
        if target_class:
            return target_class()
        return None
    
    @classmethod
    def list_targets(cls) -> dict:
        """
        List all registered targets.
        
        Returns:
            Dictionary of target types to target classes
        """
        return cls._targets.copy()
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered targets (mainly for testing)."""
        cls._targets.clear()
