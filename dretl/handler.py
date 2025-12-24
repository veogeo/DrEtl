"""
Base Handler class for READ-ONLY dataset inspection.

Handlers are responsible for detecting and inspecting datasets,
producing a DatasetReport that describes the dataset structure.
"""

from abc import ABC, abstractmethod
from typing import Optional
from dretl.models import DatasetReport


class Handler(ABC):
    """
    Abstract base class for dataset handlers.
    
    Handlers are READ-ONLY inspectors that analyze a data source
    and produce a DatasetReport describing its structure.
    """
    
    @classmethod
    @abstractmethod
    def can_handle(cls, source_path: str) -> bool:
        """
        Check if this handler can process the given source.
        
        Args:
            source_path: Path or connection string to the data source
            
        Returns:
            True if this handler can process the source
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_source_type(cls) -> str:
        """
        Get the source type identifier for this handler.
        
        Returns:
            Source type string (e.g., "gpkg", "shapefile", "postgis")
        """
        pass
    
    @abstractmethod
    def inspect(self, source_path: str, **kwargs) -> DatasetReport:
        """
        Inspect a data source and generate a report.
        
        Args:
            source_path: Path or connection string to the data source
            **kwargs: Additional handler-specific options
            
        Returns:
            DatasetReport describing the dataset structure
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type={self.get_source_type()})"


class HandlerRegistry:
    """Registry for managing available handlers."""
    
    _handlers = []
    
    @classmethod
    def register(cls, handler_class: type) -> None:
        """
        Register a handler class.
        
        Args:
            handler_class: Handler class to register
        """
        if not issubclass(handler_class, Handler):
            raise ValueError(f"{handler_class} must be a subclass of Handler")
        if handler_class not in cls._handlers:
            cls._handlers.append(handler_class)
    
    @classmethod
    def get_handler(cls, source_path: str) -> Optional[Handler]:
        """
        Get the appropriate handler for a source.
        
        Args:
            source_path: Path or connection string to the data source
            
        Returns:
            Handler instance if a suitable handler is found, None otherwise
        """
        for handler_class in cls._handlers:
            if handler_class.can_handle(source_path):
                return handler_class()
        return None
    
    @classmethod
    def list_handlers(cls) -> list:
        """
        List all registered handlers.
        
        Returns:
            List of registered handler classes
        """
        return cls._handlers.copy()
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered handlers (mainly for testing)."""
        cls._handlers.clear()
