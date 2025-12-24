"""Tests for Pipeline orchestrator."""

import pytest
from dretl.pipeline import Pipeline
from dretl.handler import Handler, HandlerRegistry
from dretl.target import Target, TargetRegistry
from dretl.models import (
    DatasetReport,
    RewritePlan,
    RewriteOptions,
    LayerInfo,
    GeometryType,
)


class MockHandler(Handler):
    """Mock handler for testing."""
    
    @classmethod
    def can_handle(cls, source_path: str) -> bool:
        return source_path.endswith('.mock')
    
    @classmethod
    def get_source_type(cls) -> str:
        return "mock"
    
    def inspect(self, source_path: str, **kwargs) -> DatasetReport:
        layer = LayerInfo(
            name="test_layer",
            geometry_type=GeometryType.POINT,
            feature_count=10
        )
        return DatasetReport(
            source_path=source_path,
            source_type=self.get_source_type(),
            layers=[layer]
        )


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


@pytest.fixture(autouse=True)
def setup_registries():
    """Setup test handlers and targets."""
    HandlerRegistry.clear()
    TargetRegistry.clear()
    
    HandlerRegistry.register(MockHandler)
    TargetRegistry.register(MockTarget)
    
    yield
    
    HandlerRegistry.clear()
    TargetRegistry.clear()


def test_pipeline_detect():
    """Test pipeline detect phase."""
    pipeline = Pipeline()
    
    report = pipeline.detect("test.mock")
    
    assert isinstance(report, DatasetReport)
    assert report.source_path == "test.mock"
    assert report.source_type == "mock"
    assert len(report.layers) == 1


def test_pipeline_detect_no_handler():
    """Test pipeline detect with no matching handler."""
    pipeline = Pipeline()
    
    with pytest.raises(ValueError, match="No handler found"):
        pipeline.detect("test.unknown")


def test_pipeline_plan():
    """Test pipeline plan phase."""
    pipeline = Pipeline()
    
    report = DatasetReport(
        source_path="test.mock",
        source_type="mock",
        layers=[
            LayerInfo(
                name="layer1",
                geometry_type=GeometryType.POINT,
                feature_count=5
            )
        ]
    )
    
    plan = pipeline.plan(
        report=report,
        target_type="mock",
        target_path="/path/to/target"
    )
    
    assert isinstance(plan, RewritePlan)
    assert plan.report == report
    assert plan.target_type == "mock"
    assert plan.target_path == "/path/to/target"


def test_pipeline_plan_with_options():
    """Test pipeline plan with custom options."""
    pipeline = Pipeline()
    
    report = DatasetReport(
        source_path="test.mock",
        source_type="mock"
    )
    
    options = RewriteOptions(srid=3857, chunk_size=500)
    
    plan = pipeline.plan(
        report=report,
        target_type="mock",
        target_path="/path/to/target",
        options=options
    )
    
    assert plan.options.srid == 3857
    assert plan.options.chunk_size == 500


def test_pipeline_plan_invalid_report():
    """Test pipeline plan with invalid report."""
    pipeline = Pipeline()
    
    report = DatasetReport(
        source_path="test.mock",
        source_type="mock",
        errors=["Test error"]
    )
    
    with pytest.raises(ValueError, match="invalid report"):
        pipeline.plan(
            report=report,
            target_type="mock",
            target_path="/path/to/target"
        )


def test_pipeline_plan_unknown_target():
    """Test pipeline plan with unknown target type."""
    pipeline = Pipeline()
    
    report = DatasetReport(
        source_path="test.mock",
        source_type="mock"
    )
    
    with pytest.raises(ValueError, match="Unknown target type"):
        pipeline.plan(
            report=report,
            target_type="unknown",
            target_path="/path/to/target"
        )


def test_pipeline_load():
    """Test pipeline load phase."""
    pipeline = Pipeline()
    
    report = DatasetReport(
        source_path="test.mock",
        source_type="mock",
        layers=[
            LayerInfo(
                name="layer1",
                geometry_type=GeometryType.POINT,
                feature_count=10
            )
        ]
    )
    
    plan = RewritePlan(
        report=report,
        target_type="mock",
        target_path="/path/to/target"
    )
    
    results = pipeline.load(plan)
    
    assert isinstance(results, dict)
    assert results["target_path"] == "/path/to/target"
    assert "layer1" in results["layers_written"]


def test_pipeline_load_no_target():
    """Test pipeline load with no matching target."""
    pipeline = Pipeline()
    
    report = DatasetReport(
        source_path="test.mock",
        source_type="mock"
    )
    
    plan = RewritePlan(
        report=report,
        target_type="unknown",
        target_path="/path/to/target"
    )
    
    with pytest.raises(ValueError, match="No target found"):
        pipeline.load(plan)


def test_pipeline_execute():
    """Test pipeline execute (all phases)."""
    pipeline = Pipeline()
    
    results = pipeline.execute(
        source_path="test.mock",
        target_type="mock",
        target_path="/path/to/target"
    )
    
    assert isinstance(results, dict)
    assert "report" in results
    assert "layers_written" in results
    assert len(results["layers_written"]) == 1
    assert "test_layer" in results["layers_written"]


def test_pipeline_execute_with_options():
    """Test pipeline execute with custom options."""
    pipeline = Pipeline()
    
    options = RewriteOptions(srid=4326)
    
    results = pipeline.execute(
        source_path="test.mock",
        target_type="mock",
        target_path="/path/to/target",
        options=options
    )
    
    assert isinstance(results, dict)
    assert "report" in results
