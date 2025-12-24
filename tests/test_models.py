"""Tests for DRETL core models."""

import pytest
from dretl.models import (
    DatasetReport,
    LayerInfo,
    FieldInfo,
    RewritePlan,
    RewriteOptions,
    GeometryType,
    FieldType,
)


def test_field_info_creation():
    """Test FieldInfo creation and serialization."""
    field = FieldInfo(
        name="population",
        field_type=FieldType.INTEGER,
        nullable=True
    )
    
    assert field.name == "population"
    assert field.field_type == FieldType.INTEGER
    assert field.nullable is True
    
    # Test serialization
    field_dict = field.to_dict()
    assert field_dict["name"] == "population"
    assert field_dict["type"] == "integer"


def test_layer_info_creation():
    """Test LayerInfo creation and serialization."""
    fields = [
        FieldInfo(name="id", field_type=FieldType.INTEGER),
        FieldInfo(name="name", field_type=FieldType.STRING),
    ]
    
    layer = LayerInfo(
        name="cities",
        geometry_type=GeometryType.POINT,
        feature_count=100,
        crs="EPSG:4326",
        fields=fields
    )
    
    assert layer.name == "cities"
    assert layer.geometry_type == GeometryType.POINT
    assert layer.feature_count == 100
    assert layer.crs == "EPSG:4326"
    assert len(layer.fields) == 2
    
    # Test serialization
    layer_dict = layer.to_dict()
    assert layer_dict["name"] == "cities"
    assert layer_dict["geometry_type"] == "Point"
    assert len(layer_dict["fields"]) == 2


def test_dataset_report_creation():
    """Test DatasetReport creation."""
    report = DatasetReport(
        source_path="/path/to/data.gpkg",
        source_type="gpkg"
    )
    
    assert report.source_path == "/path/to/data.gpkg"
    assert report.source_type == "gpkg"
    assert report.layer_count == 0
    assert report.is_valid is True  # No errors
    
    # Add an error
    report.errors.append("Test error")
    assert report.is_valid is False


def test_dataset_report_with_layers():
    """Test DatasetReport with layers."""
    layer = LayerInfo(
        name="test_layer",
        geometry_type=GeometryType.POLYGON,
        feature_count=50
    )
    
    report = DatasetReport(
        source_path="/path/to/data.gpkg",
        source_type="gpkg",
        layers=[layer]
    )
    
    assert report.layer_count == 1
    assert report.layers[0].name == "test_layer"


def test_rewrite_options():
    """Test RewriteOptions creation and defaults."""
    # Test defaults
    options = RewriteOptions()
    assert options.overwrite is True
    assert options.append is False
    assert options.chunk_size == 1000
    
    # Test custom values
    options = RewriteOptions(
        srid=3857,
        overwrite=False,
        chunk_size=500
    )
    assert options.srid == 3857
    assert options.overwrite is False
    assert options.chunk_size == 500


def test_rewrite_plan_creation():
    """Test RewritePlan creation."""
    report = DatasetReport(
        source_path="/path/to/source.gpkg",
        source_type="gpkg"
    )
    
    options = RewriteOptions(srid=4326)
    
    plan = RewritePlan(
        report=report,
        target_type="postgis",
        target_path="postgresql://localhost/db",
        options=options
    )
    
    assert plan.report == report
    assert plan.target_type == "postgis"
    assert plan.target_path == "postgresql://localhost/db"
    assert plan.options.srid == 4326


def test_rewrite_plan_layer_filtering():
    """Test RewritePlan layer filtering."""
    layer1 = LayerInfo(name="layer1", geometry_type=GeometryType.POINT, feature_count=10)
    layer2 = LayerInfo(name="layer2", geometry_type=GeometryType.POLYGON, feature_count=20)
    layer3 = LayerInfo(name="layer3", geometry_type=GeometryType.LINESTRING, feature_count=30)
    
    report = DatasetReport(
        source_path="/path/to/data.gpkg",
        source_type="gpkg",
        layers=[layer1, layer2, layer3]
    )
    
    # Test with no selection (all layers)
    plan = RewritePlan(
        report=report,
        target_type="gpkg",
        target_path="/path/to/output.gpkg"
    )
    assert len(plan.layers_to_process) == 3
    
    # Test with specific layers selected
    plan = RewritePlan(
        report=report,
        target_type="gpkg",
        target_path="/path/to/output.gpkg",
        selected_layers=["layer1", "layer3"]
    )
    layers = plan.layers_to_process
    assert len(layers) == 2
    assert layers[0].name == "layer1"
    assert layers[1].name == "layer3"


def test_geometry_types():
    """Test GeometryType enum."""
    assert GeometryType.POINT.value == "Point"
    assert GeometryType.POLYGON.value == "Polygon"
    assert GeometryType.MULTILINESTRING.value == "MultiLineString"


def test_field_types():
    """Test FieldType enum."""
    assert FieldType.STRING.value == "string"
    assert FieldType.INTEGER.value == "integer"
    assert FieldType.GEOMETRY.value == "geometry"
