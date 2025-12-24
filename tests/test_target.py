"""Tests for Target and TargetRegistry."""

import pytest
from dretl.target import Target, TargetRegistry
from dretl.models import RewritePlan, DatasetReport, RewriteOptions


class MockTarget(Target):
    """Mock target for testing."""
    
    @classmethod
    def get_target_type(cls) -> str:
        return "mock"
    
    def load(self, plan: RewritePlan, **kwargs) -> dict:
        return {
            "target_path": plan.target_path,
            "layers_written": [layer.name for layer in plan.layers_to_process],
            "errors": [],
            "warnings": [],
        }


class AnotherMockTarget(Target):
    """Another mock target for testing."""
    
    @classmethod
    def get_target_type(cls) -> str:
        return "other"
    
    def load(self, plan: RewritePlan, **kwargs) -> dict:
        return {
            "target_path": plan.target_path,
            "layers_written": [],
            "errors": [],
            "warnings": [],
        }


@pytest.fixture(autouse=True)
def clear_registry():
    """Clear the target registry before and after each test."""
    TargetRegistry.clear()
    yield
    TargetRegistry.clear()


def test_target_registration():
    """Test registering targets."""
    TargetRegistry.register(MockTarget)
    
    targets = TargetRegistry.list_targets()
    assert len(targets) == 1
    assert "mock" in targets
    assert targets["mock"] == MockTarget


def test_multiple_target_registration():
    """Test registering multiple targets."""
    TargetRegistry.register(MockTarget)
    TargetRegistry.register(AnotherMockTarget)
    
    targets = TargetRegistry.list_targets()
    assert len(targets) == 2
    assert "mock" in targets
    assert "other" in targets


def test_get_target():
    """Test getting target by type."""
    TargetRegistry.register(MockTarget)
    TargetRegistry.register(AnotherMockTarget)
    
    # Test getting mock target
    target = TargetRegistry.get_target("mock")
    assert target is not None
    assert isinstance(target, MockTarget)
    
    # Test getting other target
    target = TargetRegistry.get_target("other")
    assert target is not None
    assert isinstance(target, AnotherMockTarget)
    
    # Test no matching target
    target = TargetRegistry.get_target("unknown")
    assert target is None


def test_target_load():
    """Test target load method."""
    report = DatasetReport(
        source_path="test.mock",
        source_type="mock"
    )
    
    plan = RewritePlan(
        report=report,
        target_type="mock",
        target_path="/path/to/target"
    )
    
    target = MockTarget()
    results = target.load(plan)
    
    assert isinstance(results, dict)
    assert results["target_path"] == "/path/to/target"
    assert "layers_written" in results
    assert "errors" in results


def test_target_repr():
    """Test target string representation."""
    target = MockTarget()
    assert "MockTarget" in repr(target)
    assert "mock" in repr(target)


def test_invalid_target_registration():
    """Test that registering non-Target class raises error."""
    class NotATarget:
        pass
    
    with pytest.raises(ValueError):
        TargetRegistry.register(NotATarget)
