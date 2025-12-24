"""
GeoJSON handler for reading GeoJSON files.
"""

import os
import json
from typing import List
import fiona
from dretl.handler import Handler
from dretl.models import (
    DatasetReport,
    LayerInfo,
    FieldInfo,
    GeometryType,
    FieldType,
)


class GeoJSONHandler(Handler):
    """Handler for GeoJSON (.geojson, .json) files."""
    
    @classmethod
    def can_handle(cls, source_path: str) -> bool:
        """Check if this is a GeoJSON file."""
        if not isinstance(source_path, str) or not os.path.isfile(source_path):
            return False
        
        # Check by extension
        if source_path.lower().endswith(('.geojson', '.json')):
            # For .json files, try to peek at content to confirm it's GeoJSON
            if source_path.lower().endswith('.json'):
                try:
                    with open(source_path, 'r') as f:
                        data = json.load(f)
                        return data.get('type') in ['FeatureCollection', 'Feature']
                except:
                    return False
            return True
        
        return False
    
    @classmethod
    def get_source_type(cls) -> str:
        """Return the source type identifier."""
        return "geojson"
    
    def inspect(self, source_path: str, **kwargs) -> DatasetReport:
        """
        Inspect a GeoJSON file and generate a report.
        
        Args:
            source_path: Path to the .geojson or .json file
            **kwargs: Additional options (unused)
            
        Returns:
            DatasetReport describing the GeoJSON
        """
        report = DatasetReport(
            source_path=source_path,
            source_type=self.get_source_type(),
        )
        
        try:
            # GeoJSON files contain a single layer
            layer_name = os.path.splitext(os.path.basename(source_path))[0]
            layer_info = self._inspect_layer(source_path, layer_name)
            report.layers.append(layer_info)
                
        except Exception as e:
            report.errors.append(f"Failed to open GeoJSON: {str(e)}")
        
        return report
    
    def _inspect_layer(self, source_path: str, layer_name: str) -> LayerInfo:
        """Inspect the GeoJSON layer."""
        with fiona.open(source_path) as src:
            # Get geometry type
            geom_type_str = src.schema.get('geometry', 'Unknown')
            geometry_type = self._map_geometry_type(geom_type_str)
            
            # Get CRS
            crs = src.crs.to_string() if src.crs else "EPSG:4326"  # GeoJSON default
            
            # Get bounds
            bbox = src.bounds if hasattr(src, 'bounds') else None
            
            # Get feature count
            feature_count = len(src)
            
            # Get fields
            fields = self._extract_fields(src.schema.get('properties', {}))
            
            return LayerInfo(
                name=layer_name,
                geometry_type=geometry_type,
                feature_count=feature_count,
                crs=crs,
                bbox=bbox,
                fields=fields,
            )
    
    def _extract_fields(self, properties: dict) -> List[FieldInfo]:
        """Extract field information from schema properties."""
        fields = []
        for field_name, field_type_str in properties.items():
            field_type = self._map_field_type(field_type_str)
            fields.append(
                FieldInfo(
                    name=field_name,
                    field_type=field_type,
                )
            )
        return fields
    
    def _map_geometry_type(self, geom_type_str: str) -> GeometryType:
        """Map Fiona geometry type string to GeometryType enum."""
        mapping = {
            'Point': GeometryType.POINT,
            'LineString': GeometryType.LINESTRING,
            'Polygon': GeometryType.POLYGON,
            'MultiPoint': GeometryType.MULTIPOINT,
            'MultiLineString': GeometryType.MULTILINESTRING,
            'MultiPolygon': GeometryType.MULTIPOLYGON,
            'GeometryCollection': GeometryType.GEOMETRYCOLLECTION,
            '3D Point': GeometryType.POINT,
            '3D LineString': GeometryType.LINESTRING,
            '3D Polygon': GeometryType.POLYGON,
            '3D MultiPoint': GeometryType.MULTIPOINT,
            '3D MultiLineString': GeometryType.MULTILINESTRING,
            '3D MultiPolygon': GeometryType.MULTIPOLYGON,
        }
        return mapping.get(geom_type_str, GeometryType.UNKNOWN)
    
    def _map_field_type(self, field_type_str: str) -> FieldType:
        """Map Fiona field type string to FieldType enum."""
        field_type_lower = field_type_str.lower() if isinstance(field_type_str, str) else ''
        
        if 'int' in field_type_lower:
            return FieldType.INTEGER
        elif 'float' in field_type_lower or 'real' in field_type_lower:
            return FieldType.FLOAT
        elif 'str' in field_type_lower or 'text' in field_type_lower:
            return FieldType.STRING
        elif 'bool' in field_type_lower:
            return FieldType.BOOLEAN
        elif 'date' in field_type_lower and 'time' not in field_type_lower:
            return FieldType.DATE
        elif 'date' in field_type_lower or 'time' in field_type_lower:
            return FieldType.DATETIME
        else:
            return FieldType.UNKNOWN
