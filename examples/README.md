# DRETL Examples

This directory contains example files and scripts demonstrating how to use DRETL.

## Files

- `cities.geojson` - Sample GeoJSON file with 3 city points
- `example_usage.py` - Python script demonstrating DRETL API usage

## Running the Examples

### Using the Python API

Run the example script:

```bash
python examples/example_usage.py
```

This will demonstrate:
1. Inspecting a dataset
2. Converting GeoJSON to GeoPackage
3. Using the three-phase pipeline (detect → plan → load)

### Using the CLI

Inspect the sample data:

```bash
dretl inspect examples/cities.geojson
```

Convert to GeoPackage:

```bash
dretl convert examples/cities.geojson gpkg examples/output.gpkg
```

Convert with options:

```bash
dretl convert examples/cities.geojson gpkg examples/output.gpkg --srid 3857 --chunk-size 100
```

List available formats:

```bash
dretl list-handlers
dretl list-targets
```

## Output Files

Generated output files are automatically excluded by `.gitignore`:
- `*.gpkg` files
- `output*.geojson` files
