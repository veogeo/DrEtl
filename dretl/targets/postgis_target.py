"""
PostGIS target for writing to PostgreSQL/PostGIS databases.
"""

import geopandas as gpd
from sqlalchemy import create_engine
from geoalchemy2 import Geometry
import fiona
from dretl.target import Target
from dretl.models import RewritePlan


class PostGISTarget(Target):
    """Target for writing to PostGIS databases."""
    
    @classmethod
    def get_target_type(cls) -> str:
        """Return the target type identifier."""
        return "postgis"
    
    def load(self, plan: RewritePlan, **kwargs) -> dict:
        """
        Execute a rewrite plan and write to PostGIS.
        
        Args:
            plan: RewritePlan with target_path as connection string
                  Format: postgresql://user:pass@host:port/dbname
            **kwargs: Additional options (schema name, etc.)
            
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
            # Create database engine
            engine = create_engine(plan.target_path)
            
            # Get schema name from kwargs or use 'public'
            schema = kwargs.get('schema', 'public')
            
            # Process each layer
            for layer_info in plan.layers_to_process:
                try:
                    self._write_layer(plan, layer_info, engine, schema)
                    results["layers_written"].append(layer_info.name)
                except Exception as e:
                    error_msg = f"Failed to write layer '{layer_info.name}': {str(e)}"
                    results["errors"].append(error_msg)
            
            # Close engine
            engine.dispose()
            
        except Exception as e:
            results["errors"].append(f"Failed to connect to PostGIS: {str(e)}")
        
        return results
    
    def _write_layer(self, plan: RewritePlan, layer_info, engine, schema):
        """Write a single layer to PostGIS."""
        # Read source data using geopandas for easier PostGIS writing
        gdf = gpd.read_file(plan.report.source_path, layer=layer_info.name)
        
        # Determine target table name
        table_name = plan.options.layer_name or layer_info.name
        
        # Determine write mode
        if_exists = 'replace'  # default
        if plan.options.append:
            if_exists = 'append'
        elif plan.options.truncate:
            if_exists = 'replace'
        elif not plan.options.overwrite:
            if_exists = 'fail'
        
        # Handle SRID transformation
        if plan.options.srid:
            target_crs = f"EPSG:{plan.options.srid}"
            if gdf.crs is None:
                gdf.set_crs(target_crs, inplace=True)
            else:
                gdf = gdf.to_crs(target_crs)
        
        # Write to PostGIS
        gdf.to_postgis(
            name=table_name,
            con=engine,
            schema=schema,
            if_exists=if_exists,
            index=False,
            chunksize=plan.options.chunk_size,
        )
