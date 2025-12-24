"""
Pipeline orchestrator for the ETL process.

The Pipeline coordinates the three phases:
1. Detect - Use handlers to inspect source datasets
2. Rewrite - Create transformation plans
3. Load - Execute plans using targets
"""

from typing import Optional, Dict, Any
from dretl.models import DatasetReport, RewritePlan, RewriteOptions
from dretl.handler import HandlerRegistry
from dretl.target import TargetRegistry


class Pipeline:
    """
    ETL Pipeline orchestrator.
    
    Coordinates the detect → rewrite → load workflow for geospatial datasets.
    """
    
    def __init__(self):
        """Initialize the pipeline."""
        self.handler_registry = HandlerRegistry
        self.target_registry = TargetRegistry
    
    def detect(self, source_path: str, **kwargs) -> DatasetReport:
        """
        Phase 1: Detect and inspect a dataset.
        
        Args:
            source_path: Path or connection string to the data source
            **kwargs: Additional handler-specific options
            
        Returns:
            DatasetReport describing the dataset
            
        Raises:
            ValueError: If no suitable handler is found
        """
        handler = self.handler_registry.get_handler(source_path)
        if handler is None:
            raise ValueError(f"No handler found for source: {source_path}")
        
        return handler.inspect(source_path, **kwargs)
    
    def plan(
        self,
        report: DatasetReport,
        target_type: str,
        target_path: str,
        options: Optional[RewriteOptions] = None,
        selected_layers: Optional[list] = None,
    ) -> RewritePlan:
        """
        Phase 2: Create a rewrite plan from a dataset report.
        
        Args:
            report: DatasetReport from the detect phase
            target_type: Target type (e.g., "postgis", "gpkg")
            target_path: Target path or connection string
            options: Rewrite options
            selected_layers: List of layer names to process (None = all)
            
        Returns:
            RewritePlan ready for execution
            
        Raises:
            ValueError: If the report is invalid or target type is unknown
        """
        if not report.is_valid:
            raise ValueError(
                f"Cannot create plan from invalid report. Errors: {report.errors}"
            )
        
        # Verify target type exists
        if self.target_registry.get_target(target_type) is None:
            raise ValueError(f"Unknown target type: {target_type}")
        
        if options is None:
            options = RewriteOptions()
        
        return RewritePlan(
            report=report,
            target_type=target_type,
            target_path=target_path,
            options=options,
            selected_layers=selected_layers,
        )
    
    def load(self, plan: RewritePlan, **kwargs) -> Dict[str, Any]:
        """
        Phase 3: Execute a rewrite plan.
        
        Args:
            plan: RewritePlan to execute
            **kwargs: Additional target-specific options
            
        Returns:
            Dictionary with execution results
            
        Raises:
            ValueError: If no suitable target is found
        """
        target = self.target_registry.get_target(plan.target_type)
        if target is None:
            raise ValueError(f"No target found for type: {plan.target_type}")
        
        return target.load(plan, **kwargs)
    
    def execute(
        self,
        source_path: str,
        target_type: str,
        target_path: str,
        options: Optional[RewriteOptions] = None,
        selected_layers: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute the complete ETL pipeline in one call.
        
        Args:
            source_path: Source dataset path
            target_type: Target type
            target_path: Target path or connection string
            options: Rewrite options
            selected_layers: List of layer names to process
            **kwargs: Additional options for handlers/targets
            
        Returns:
            Dictionary with execution results including the report
        """
        # Phase 1: Detect
        report = self.detect(source_path, **kwargs)
        
        # Phase 2: Plan
        plan = self.plan(
            report=report,
            target_type=target_type,
            target_path=target_path,
            options=options,
            selected_layers=selected_layers,
        )
        
        # Phase 3: Load
        results = self.load(plan, **kwargs)
        
        # Add report to results
        results["report"] = report.to_dict()
        
        return results
