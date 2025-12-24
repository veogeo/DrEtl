"""Handlers package for various geospatial data sources."""

from dretl.handlers.gpkg_handler import GeoPackageHandler
from dretl.handlers.shapefile_handler import ShapefileHandler
from dretl.handlers.geojson_handler import GeoJSONHandler

__all__ = [
    "GeoPackageHandler",
    "ShapefileHandler",
    "GeoJSONHandler",
]
