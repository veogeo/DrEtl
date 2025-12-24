"""
GeoPackage target for writing to GPKG files.
"""

import os
import fiona
from fiona.crs import from_string
import geopandas as gpd
from dretl.target import Target
from dretl.models import RewritePlan


class GeoPackageTarget(Target):
    """Target for writing to GeoPackage (.gpkg) files."""
    
    @classmethod
    def get_target_type(cls) -> str:
        """Return the target type identifier."""
        return "gpkg"
    
    def load(self, plan: RewritePlan, **kwargs) -> dict:
        """
        Execute a rewrite plan and write to GeoPackage.
        
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
        
        try:
            # Ensure parent directory exists
            parent_dir = os.path.dirname(plan.target_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
            
            # Process each layer
            for layer_info in plan.layers_to_process:
                try:
                    self._write_layer(plan, layer_info)
                    results["layers_written"].append(layer_info.name)
                except Exception as e:
                    error_msg = f"Failed to write layer '{layer_info.name}': {str(e)}"
                    results["errors"].append(error_msg)
            
        except Exception as e:
            results["errors"].append(f"Failed to write to GeoPackage: {str(e)}")
        
        return results
    
    def _write_layer(self, plan: RewritePlan, layer_info):
        """Write a single layer to the GeoPackage."""
        # Read source data
        with fiona.open(plan.report.source_path, layer=layer_info.name) as src:
            # Determine target layer name
            target_layer = plan.options.layer_name or layer_info.name
            
            # Determine write mode
            mode = 'w'
            if os.path.exists(plan.target_path):
                # File exists, check if we should append or overwrite
                if plan.options.append:
                    mode = 'a'
                elif not plan.options.overwrite:
                    raise ValueError(
                        f"Target file exists and overwrite=False: {plan.target_path}"
                    )
            
            # Get schema and CRS
            schema = src.schema.copy()
            crs = src.crs
            
            # Apply SRID transformation if requested
            if plan.options.srid:
                crs = from_string(f"EPSG:{plan.options.srid}")
            
            # Write features
            with fiona.open(
                plan.target_path,
                mode,
                driver='GPKG',
                layer=target_layer,
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
