# DRETL - Data Rewrite ETL

**DRETL** (Data Rewrite ETL) is an on-demand batch ETL engine for geospatial datasets. It provides a clean, extensible framework for transforming geospatial data between different formats and backends (e.g., GPKG → PostGIS, Shapefile → GeoJSON).

This is a framework-agnostic alternative to GeoNode Importer, with no Django or GeoNode dependencies.

## Features

- 🔍 **READ-ONLY Handlers**: Inspect and analyze geospatial datasets
- 📝 **WRITE-ONLY Targets**: Load data into various backends
- 🔄 **Pipeline Architecture**: Clean detect → rewrite → load workflow
- 🔌 **Extensible Design**: Easy to add new handlers and targets
- 🖥️ **CLI Interface**: Simple command-line tools for common tasks
- 🐍 **Pure Python**: No external framework dependencies

## Architecture

DRETL follows a three-phase pipeline:

1. **Detect**: Handlers inspect the source dataset and produce a `DatasetReport`
2. **Rewrite**: A `RewritePlan` is created from the report with transformation instructions
3. **Load**: Targets execute the plan and write data to the destination

### Key Components

- **Handler**: READ-ONLY inspector that analyzes a data source
- **Target**: WRITE-ONLY loader that writes to a backend
- **DatasetReport**: Describes the structure of a dataset (layers, fields, CRS, etc.)
- **RewritePlan**: Instructions for how to transform and load data
- **Pipeline**: Orchestrates the entire ETL process

## Installation

```bash
# Install from source
git clone https://github.com/veogeo/DrEtl.git
cd DrEtl
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## Quick Start

### Command Line

Inspect a dataset:
```bash
dretl inspect data.gpkg
```

Convert between formats:
```bash
# GPKG to GeoJSON
dretl convert data.gpkg geojson output.geojson

# Shapefile to PostGIS
dretl convert data.shp postgis "postgresql://user:pass@localhost/db"

# GPKG to GPKG (specific layers)
dretl convert input.gpkg gpkg output.gpkg --layer cities --layer roads
```

List available handlers and targets:
```bash
dretl list-handlers
dretl list-targets
```

### Python API

```python
from dretl import Pipeline, RewriteOptions

# Initialize pipeline
pipeline = Pipeline()

# Phase 1: Detect
report = pipeline.detect("input.gpkg")
print(f"Found {report.layer_count} layers")

# Phase 2: Plan
plan = pipeline.plan(
    report=report,
    target_type="postgis",
    target_path="postgresql://user:pass@localhost/db",
    options=RewriteOptions(srid=4326, overwrite=True)
)

# Phase 3: Load
results = pipeline.load(plan, schema="public")
print(f"Written {len(results['layers_written'])} layers")

# Or execute all phases at once
results = pipeline.execute(
    source_path="input.gpkg",
    target_type="geojson",
    target_path="output.geojson"
)
```

## Supported Formats

### Handlers (Read)
- **GeoPackage** (.gpkg)
- **Shapefile** (.shp)
- **GeoJSON** (.geojson, .json)

### Targets (Write)
- **GeoPackage** (.gpkg)
- **GeoJSON** (.geojson)
- **PostGIS** (PostgreSQL/PostGIS)

## Extending DRETL

### Creating a Custom Handler

```python
from dretl.handler import Handler, HandlerRegistry
from dretl.models import DatasetReport

class MyHandler(Handler):
    @classmethod
    def can_handle(cls, source_path: str) -> bool:
        return source_path.endswith('.myformat')
    
    @classmethod
    def get_source_type(cls) -> str:
        return "myformat"
    
    def inspect(self, source_path: str, **kwargs) -> DatasetReport:
        # Implement inspection logic
        report = DatasetReport(
            source_path=source_path,
            source_type=self.get_source_type()
        )
        # ... populate report
        return report

# Register the handler
HandlerRegistry.register(MyHandler)
```

### Creating a Custom Target

```python
from dretl.target import Target, TargetRegistry
from dretl.models import RewritePlan

class MyTarget(Target):
    @classmethod
    def get_target_type(cls) -> str:
        return "mybackend"
    
    def load(self, plan: RewritePlan, **kwargs) -> dict:
        # Implement loading logic
        results = {
            "layers_written": [],
            "errors": [],
            "warnings": []
        }
        # ... execute plan
        return results

# Register the target
TargetRegistry.register(MyTarget)
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black dretl/

# Lint code
ruff dretl/
```

## Design Principles

- **Separation of Concerns**: Handlers only read, targets only write
- **Framework Agnostic**: No Django, GeoNode, or other framework dependencies
- **Extensible**: Easy plugin system for new formats and backends
- **Type Safety**: Use of dataclasses and enums for clear data structures
- **Clean API**: Simple, intuitive interfaces for both CLI and Python usage

## License

Apache License 2.0 - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Comparison with GeoNode Importer

DRETL is inspired by GeoNode Importer but designed to be:
- **Framework-agnostic**: No Django or GeoNode required
- **Lightweight**: Minimal dependencies, focused on ETL operations
- **Extensible**: Clean plugin architecture for handlers and targets
- **Standalone**: Can be used in any Python project or as a CLI tool