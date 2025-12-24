"""
GeoJSON target for writing to GeoJSON files.
"""

import os
import fiona
from fiona.crs import from_string
from dretl.target import Target
from dretl.models import RewritePlan


class GeoJSONTarget(Target):
    """Target for writing to GeoJSON (.geojson) files."""
    
    @classmethod
    def get_target_type(cls) -> str:
        """Return the target type identifier."""
        return "geojson"
    
    def load(self, plan: RewritePlan, **kwargs) -> dict:
        """
        Execute a rewrite plan and write to GeoJSON.
        
        Args:
            plan: RewritePlan describing the data transformation
            **kwargs: Additional options (unused)
            
        Returns:
            Dictionary with execution results
        """
        results = {
            "target_path": plan.target_path,
            "layers_written": [],
            "errors": [],
            "warnings": [],
        }
        
        # GeoJSON only supports a single layer
        layers = plan.layers_to_process
        if len(layers) > 1:
            results["warnings"].append(
                f"GeoJSON supports only one layer. Writing first layer: {layers[0].name}"
            )
        
        if not layers:
            results["errors"].append("No layers to write")
            return results
        
        try:
            # Ensure parent directory exists
            parent_dir = os.path.dirname(plan.target_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
            
            # Write the first layer
            layer_info = layers[0]
            try:
                self._write_layer(plan, layer_info)
                results["layers_written"].append(layer_info.name)
            except Exception as e:
                error_msg = f"Failed to write layer '{layer_info.name}': {str(e)}"
                results["errors"].append(error_msg)
            
        except Exception as e:
            results["errors"].append(f"Failed to write to GeoJSON: {str(e)}")
        
        return results
    
    def _write_layer(self, plan: RewritePlan, layer_info):
        """Write a single layer to GeoJSON."""
        # Read source data
        with fiona.open(plan.report.source_path, layer=layer_info.name) as src:
            # Get schema and CRS
            schema = src.schema.copy()
            crs = src.crs or from_string("EPSG:4326")  # GeoJSON default
            
            # Apply SRID transformation if requested
            if plan.options.srid:
                crs = from_string(f"EPSG:{plan.options.srid}")
            
            # Check if file exists
            if os.path.exists(plan.target_path) and not plan.options.overwrite:
                raise ValueError(
                    f"Target file exists and overwrite=False: {plan.target_path}"
                )
            
            # Write features
            with fiona.open(
                plan.target_path,
                'w',
                driver='GeoJSON',
                schema=schema,
                crs=crs,
            ) as dst:
                # Write in chunks
                chunk = []
                for i, feature in enumerate(src):
                    chunk.append(feature)
                    
                    if len(chunk) >= plan.options.chunk_size:
                        dst.writerecords(chunk)
                        chunk = []
                
                # Write remaining features
                if chunk:
                    dst.writerecords(chunk)
