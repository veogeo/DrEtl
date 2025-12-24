"""Tests for Handler and HandlerRegistry."""

import pytest
from dretl.handler import Handler, HandlerRegistry
from dretl.models import DatasetReport


class MockHandler(Handler):
    """Mock handler for testing."""
    
    @classmethod
    def can_handle(cls, source_path: str) -> bool:
        return source_path.endswith('.mock')
    
    @classmethod
    def get_source_type(cls) -> str:
        return "mock"
    
    def inspect(self, source_path: str, **kwargs) -> DatasetReport:
        return DatasetReport(
            source_path=source_path,
            source_type=self.get_source_type()
        )


class AnotherMockHandler(Handler):
    """Another mock handler for testing."""
    
    @classmethod
    def can_handle(cls, source_path: str) -> bool:
        return source_path.endswith('.other')
    
    @classmethod
    def get_source_type(cls) -> str:
        return "other"
    
    def inspect(self, source_path: str, **kwargs) -> DatasetReport:
        return DatasetReport(
            source_path=source_path,
            source_type=self.get_source_type()
        )


@pytest.fixture(autouse=True)
def clear_registry():
    """Clear the handler registry before and after each test."""
    HandlerRegistry.clear()
    yield
    HandlerRegistry.clear()


def test_handler_registration():
    """Test registering handlers."""
    HandlerRegistry.register(MockHandler)
    
    handlers = HandlerRegistry.list_handlers()
    assert len(handlers) == 1
    assert MockHandler in handlers


def test_multiple_handler_registration():
    """Test registering multiple handlers."""
    HandlerRegistry.register(MockHandler)
    HandlerRegistry.register(AnotherMockHandler)
    
    handlers = HandlerRegistry.list_handlers()
    assert len(handlers) == 2


def test_duplicate_registration():
    """Test that duplicate registration doesn't add handler twice."""
    HandlerRegistry.register(MockHandler)
    HandlerRegistry.register(MockHandler)
    
    handlers = HandlerRegistry.list_handlers()
    assert len(handlers) == 1


def test_get_handler():
    """Test getting appropriate handler for source."""
    HandlerRegistry.register(MockHandler)
    HandlerRegistry.register(AnotherMockHandler)
    
    # Test getting mock handler
    handler = HandlerRegistry.get_handler("test.mock")
    assert handler is not None
    assert isinstance(handler, MockHandler)
    
    # Test getting other handler
    handler = HandlerRegistry.get_handler("test.other")
    assert handler is not None
    assert isinstance(handler, AnotherMockHandler)
    
    # Test no matching handler
    handler = HandlerRegistry.get_handler("test.unknown")
    assert handler is None


def test_handler_inspect():
    """Test handler inspect method."""
    handler = MockHandler()
    report = handler.inspect("test.mock")
    
    assert isinstance(report, DatasetReport)
    assert report.source_path == "test.mock"
    assert report.source_type == "mock"


def test_handler_repr():
    """Test handler string representation."""
    handler = MockHandler()
    assert "MockHandler" in repr(handler)
    assert "mock" in repr(handler)


def test_invalid_handler_registration():
    """Test that registering non-Handler class raises error."""
    class NotAHandler:
        pass
    
    with pytest.raises(ValueError):
        HandlerRegistry.register(NotAHandler)
