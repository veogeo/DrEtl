"""
Command-line interface for DRETL.

Provides commands for inspecting datasets and executing ETL pipelines.
"""

import json
import click
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


@click.group()
@click.version_option(version='0.1.0')
def main():
    """
    DRETL - Data Rewrite ETL
    
    An on-demand batch ETL engine for geospatial datasets.
    Framework-agnostic alternative to GeoNode Importer.
    """
    pass


@main.command()
@click.argument('source', type=click.Path(exists=True))
@click.option('--format', '-f', 'output_format', 
              type=click.Choice(['json', 'text']), 
              default='text',
              help='Output format')
def inspect(source, output_format):
    """
    Inspect a geospatial dataset and display its structure.
    
    SOURCE: Path to the dataset file or connection string
    """
    pipeline = Pipeline()
    
    try:
        # Phase 1: Detect
        click.echo(f"Inspecting: {source}")
        report = pipeline.detect(source)
        
        if output_format == 'json':
            # Output as JSON
            click.echo(json.dumps(report.to_dict(), indent=2))
        else:
            # Output as human-readable text
            _display_report(report)
        
        # Exit with error code if report has errors
        if not report.is_valid:
            raise click.ClickException("Dataset inspection failed")
            
    except Exception as e:
        raise click.ClickException(str(e))


@main.command()
@click.argument('source', type=click.Path(exists=True))
@click.argument('target-type', type=str)
@click.argument('target-path', type=str)
@click.option('--layer', '-l', multiple=True, help='Layer to process (can specify multiple)')
@click.option('--srid', type=int, help='Target SRID for reprojection')
@click.option('--append', is_flag=True, help='Append to existing data')
@click.option('--truncate', is_flag=True, help='Truncate target before writing')
@click.option('--no-overwrite', is_flag=True, help='Fail if target exists')
@click.option('--chunk-size', type=int, default=1000, help='Batch size for writing')
@click.option('--schema', type=str, help='Target schema (PostGIS only)')
def convert(source, target_type, target_path, layer, srid, append, 
            truncate, no_overwrite, chunk_size, schema):
    """
    Convert a geospatial dataset to another format/backend.
    
    SOURCE: Path to the source dataset
    
    TARGET_TYPE: Target format (gpkg, geojson, postgis)
    
    TARGET_PATH: Target path or connection string
    
    Examples:
    
      dretl convert data.shp gpkg output.gpkg
      
      dretl convert data.gpkg postgis "postgresql://user:pass@localhost/db"
      
      dretl convert data.gpkg geojson output.geojson --layer cities
    """
    pipeline = Pipeline()
    
    # Build options
    options = RewriteOptions(
        srid=srid,
        append=append,
        truncate=truncate,
        overwrite=not no_overwrite,
        chunk_size=chunk_size,
    )
    
    # Convert layers tuple to list (or None)
    selected_layers = list(layer) if layer else None
    
    try:
        click.echo(f"Converting: {source} → {target_type}:{target_path}")
        
        # Execute pipeline
        kwargs = {}
        if schema:
            kwargs['schema'] = schema
        
        results = pipeline.execute(
            source_path=source,
            target_type=target_type,
            target_path=target_path,
            options=options,
            selected_layers=selected_layers,
            **kwargs
        )
        
        # Display results
        click.echo("\n✓ Conversion complete!")
        click.echo(f"  Layers written: {len(results.get('layers_written', []))}")
        
        for layer_name in results.get('layers_written', []):
            click.echo(f"    - {layer_name}")
        
        # Display warnings
        for warning in results.get('warnings', []):
            click.echo(f"  ⚠ Warning: {warning}", err=True)
        
        # Display errors
        if results.get('errors'):
            click.echo("\n✗ Errors occurred:", err=True)
            for error in results['errors']:
                click.echo(f"  - {error}", err=True)
            raise click.ClickException("Conversion failed")
            
    except Exception as e:
        raise click.ClickException(str(e))


@main.command()
def list_handlers():
    """List all registered handlers."""
    handlers = HandlerRegistry.list_handlers()
    
    click.echo("Registered Handlers:")
    for handler_class in handlers:
        handler = handler_class()
        click.echo(f"  - {handler.get_source_type()}: {handler_class.__name__}")


@main.command()
def list_targets():
    """List all registered targets."""
    targets = TargetRegistry.list_targets()
    
    click.echo("Registered Targets:")
    for target_type, target_class in targets.items():
        click.echo(f"  - {target_type}: {target_class.__name__}")


def _display_report(report):
    """Display a dataset report in human-readable format."""
    click.echo(f"\nSource: {report.source_path}")
    click.echo(f"Type: {report.source_type}")
    click.echo(f"Layers: {report.layer_count}")
    
    if report.errors:
        click.echo("\n✗ Errors:")
        for error in report.errors:
            click.echo(f"  - {error}", err=True)
    
    if report.warnings:
        click.echo("\n⚠ Warnings:")
        for warning in report.warnings:
            click.echo(f"  - {warning}")
    
    for i, layer in enumerate(report.layers, 1):
        click.echo(f"\nLayer {i}: {layer.name}")
        click.echo(f"  Geometry: {layer.geometry_type.value}")
        click.echo(f"  Features: {layer.feature_count}")
        click.echo(f"  CRS: {layer.crs or 'Unknown'}")
        
        if layer.bbox:
            click.echo(f"  Bounds: {layer.bbox}")
        
        if layer.fields:
            click.echo(f"  Fields ({len(layer.fields)}):")
            for field in layer.fields:
                click.echo(f"    - {field.name}: {field.field_type.value}")


if __name__ == '__main__':
    main()
