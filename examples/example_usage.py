"""
Example usage of DRETL Python API.

This demonstrates the three-phase pipeline: detect → rewrite → load
"""

from dretl import Pipeline, RewriteOptions
from dretl.handler import HandlerRegistry
from dretl.target import TargetRegistry

# Import and register handlers
from dretl.handlers import GeoPackageHandler, ShapefileHandler, GeoJSONHandler
HandlerRegistry.register(GeoPackageHandler)
HandlerRegistry.register(ShapefileHandler)
HandlerRegistry.register(GeoJSONHandler)

# Import and register targets
from dretl.targets import GeoPackageTarget, GeoJSONTarget, PostGISTarget
TargetRegistry.register(GeoPackageTarget)
TargetRegistry.register(GeoJSONTarget)
TargetRegistry.register(PostGISTarget)


def example_inspect():
    """Example: Inspect a dataset."""
    print("=" * 60)
    print("Example 1: Inspecting a dataset")
    print("=" * 60)
    
    pipeline = Pipeline()
    
    # Phase 1: Detect
    report = pipeline.detect("examples/cities.geojson")
    
    print(f"\nSource: {report.source_path}")
    print(f"Type: {report.source_type}")
    print(f"Valid: {report.is_valid}")
    print(f"Layers: {report.layer_count}")
    
    for layer in report.layers:
        print(f"\nLayer: {layer.name}")
        print(f"  Geometry: {layer.geometry_type.value}")
        print(f"  Features: {layer.feature_count}")
        print(f"  CRS: {layer.crs}")
        print(f"  Fields:")
        for field in layer.fields:
            print(f"    - {field.name}: {field.field_type.value}")


def example_convert():
    """Example: Convert GeoJSON to GeoPackage."""
    print("\n" + "=" * 60)
    print("Example 2: Converting GeoJSON to GeoPackage")
    print("=" * 60)
    
    pipeline = Pipeline()
    
    # Execute complete pipeline
    results = pipeline.execute(
        source_path="examples/cities.geojson",
        target_type="gpkg",
        target_path="examples/output.gpkg",
        options=RewriteOptions(
            overwrite=True,
            srid=4326
        )
    )
    
    print(f"\nConversion complete!")
    print(f"Layers written: {results['layers_written']}")
    print(f"Errors: {results.get('errors', [])}")
    print(f"Warnings: {results.get('warnings', [])}")


def example_three_phases():
    """Example: Execute pipeline in three separate phases."""
    print("\n" + "=" * 60)
    print("Example 3: Three-phase pipeline execution")
    print("=" * 60)
    
    pipeline = Pipeline()
    
    # Phase 1: Detect
    print("\nPhase 1: Detect")
    report = pipeline.detect("examples/cities.geojson")
    print(f"  Found {report.layer_count} layer(s)")
    
    # Phase 2: Plan
    print("\nPhase 2: Plan")
    plan = pipeline.plan(
        report=report,
        target_type="gpkg",
        target_path="examples/output2.gpkg",
        options=RewriteOptions(overwrite=True)
    )
    print(f"  Will process {len(plan.layers_to_process)} layer(s)")
    
    # Phase 3: Load
    print("\nPhase 3: Load")
    results = pipeline.load(plan)
    print(f"  Written {len(results['layers_written'])} layer(s)")


if __name__ == '__main__':
    example_inspect()
    example_convert()
    example_three_phases()
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
