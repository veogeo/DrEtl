"""
DRETL - Data Rewrite ETL

An on-demand batch ETL engine for geospatial datasets.
Framework-agnostic alternative to GeoNode Importer.
"""

__version__ = "0.1.0"

from dretl.models import (
    DatasetReport,
    RewritePlan,
    LayerInfo,
    FieldInfo,
    RewriteOptions,
    GeometryType,
    FieldType,
)
from dretl.handler import Handler, HandlerRegistry
from dretl.target import Target, TargetRegistry
from dretl.pipeline import Pipeline

__all__ = [
    "DatasetReport",
    "RewritePlan",
    "LayerInfo",
    "FieldInfo",
    "RewriteOptions",
    "GeometryType",
    "FieldType",
    "Handler",
    "HandlerRegistry",
    "Target",
    "TargetRegistry",
    "Pipeline",
]
