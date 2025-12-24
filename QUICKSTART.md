# DRETL Quick Reference

## Installation

```bash
pip install dretl
# or from source
pip install -e .
```

## CLI Commands

### Inspect a Dataset
```bash
# Text output (default)
dretl inspect data.gpkg

# JSON output
dretl inspect data.gpkg --format json
```

### Convert Between Formats
```bash
# Basic conversion
dretl convert source.shp gpkg output.gpkg

# With options
dretl convert source.gpkg postgis "postgresql://user:pass@host/db" \
  --layer cities \
  --srid 4326 \
  --schema public \
  --chunk-size 1000

# GeoJSON to GPKG
dretl convert data.geojson gpkg output.gpkg

# GPKG to PostGIS
dretl convert data.gpkg postgis "postgresql://localhost/mydb"
```

### List Available Formats
```bash
dretl list-handlers  # Show supported input formats
dretl list-targets   # Show supported output formats
```

## Python API

### Basic Usage

```python
from dretl import Pipeline, RewriteOptions

# Create pipeline
pipeline = Pipeline()

# Single-step execution
results = pipeline.execute(
    source_path="data.gpkg",
    target_type="geojson",
    target_path="output.geojson"
)
```

### Three-Phase Workflow

```python
from dretl import Pipeline, RewriteOptions

pipeline = Pipeline()

# Phase 1: Detect
report = pipeline.detect("data.gpkg")
print(f"Found {report.layer_count} layers")

# Phase 2: Plan
plan = pipeline.plan(
    report=report,
    target_type="postgis",
    target_path="postgresql://localhost/db",
    options=RewriteOptions(srid=4326, overwrite=True)
)

# Phase 3: Load
results = pipeline.load(plan, schema="public")
print(f"Written {len(results['layers_written'])} layers")
```

### Working with Options

```python
from dretl import RewriteOptions

# Create options
options = RewriteOptions(
    srid=3857,              # Target SRID
    overwrite=True,         # Overwrite existing data
    append=False,           # Append to existing data
    truncate=False,         # Truncate before writing
    chunk_size=1000,        # Batch size
    layer_name="new_name"   # Rename layer
)

# Use in pipeline
results = pipeline.execute(
    source_path="data.gpkg",
    target_type="postgis",
    target_path="postgresql://localhost/db",
    options=options
)
```

### Inspecting Data

```python
report = pipeline.detect("data.gpkg")

# Report properties
print(report.source_path)
print(report.source_type)
print(report.is_valid)
print(report.layer_count)
print(report.errors)
print(report.warnings)

# Layer information
for layer in report.layers:
    print(f"Layer: {layer.name}")
    print(f"  Type: {layer.geometry_type.value}")
    print(f"  Count: {layer.feature_count}")
    print(f"  CRS: {layer.crs}")
    print(f"  Bounds: {layer.bbox}")
    
    # Field information
    for field in layer.fields:
        print(f"    {field.name}: {field.field_type.value}")
```

### Filtering Layers

```python
# Convert specific layers only
results = pipeline.execute(
    source_path="data.gpkg",
    target_type="geojson",
    target_path="output.geojson",
    selected_layers=["cities", "roads"]
)
```

## Supported Formats

### Handlers (Input)
- **gpkg** - GeoPackage files (.gpkg)
- **shapefile** - Shapefiles (.shp)
- **geojson** - GeoJSON files (.geojson, .json)

### Targets (Output)
- **gpkg** - GeoPackage files
- **geojson** - GeoJSON files
- **postgis** - PostgreSQL/PostGIS databases

## Common Patterns

### Convert Multiple Layers
```bash
# All layers
dretl convert multi.gpkg postgis "postgresql://localhost/db"

# Specific layers
dretl convert multi.gpkg postgis "postgresql://localhost/db" \
  --layer layer1 --layer layer2
```

### Coordinate Transformation
```bash
# Reproject to EPSG:3857
dretl convert data.gpkg geojson output.geojson --srid 3857
```

### Database Operations
```bash
# Overwrite (default)
dretl convert data.gpkg postgis "postgresql://localhost/db"

# Append to existing
dretl convert data.gpkg postgis "postgresql://localhost/db" --append

# Different schema
dretl convert data.gpkg postgis "postgresql://localhost/db" --schema myschema
```

## Extending DRETL

### Register Custom Handler
```python
from dretl.handler import Handler, HandlerRegistry

class MyHandler(Handler):
    @classmethod
    def can_handle(cls, source_path: str) -> bool:
        return source_path.endswith('.myformat')
    
    @classmethod
    def get_source_type(cls) -> str:
        return "myformat"
    
    def inspect(self, source_path: str, **kwargs):
        # Implementation
        pass

HandlerRegistry.register(MyHandler)
```

### Register Custom Target
```python
from dretl.target import Target, TargetRegistry

class MyTarget(Target):
    @classmethod
    def get_target_type(cls) -> str:
        return "mybackend"
    
    def load(self, plan, **kwargs):
        # Implementation
        pass

TargetRegistry.register(MyTarget)
```

## Environment Variables

None currently. All configuration is done via command-line arguments or Python API.

## Troubleshooting

### "No handler found for source"
- Check file extension
- Verify file exists
- Use `dretl list-handlers` to see supported formats

### "No target found for type"
- Check target type spelling
- Use `dretl list-targets` to see available targets

### Connection Errors (PostGIS)
- Verify connection string format: `postgresql://user:pass@host:port/database`
- Check database is accessible
- Ensure PostGIS extension is enabled

## Resources

- GitHub: https://github.com/veogeo/DrEtl
- Documentation: See README.md
- Examples: See examples/ directory
