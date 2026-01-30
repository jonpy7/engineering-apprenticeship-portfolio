"""
ETL Pipeline Orchestration

Main pipeline orchestrator that coordinates extraction, transformation, and loading.
Includes error handling, logging, and metrics tracking.
"""

import sys
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from project_etl.etl.utils import load_config, setup_logging, PipelineMetrics, ensure_directory
from extract import DataExtractor
from transform import DataTransformer
from project_etl.etl.load import DataLoader


logger = logging.getLogger("etl_pipeline.main")


class ETLPipeline:
    """
    Main ETL pipeline orchestrator.
    
    Coordinates the extraction, transformation, and loading of data
    with comprehensive error handling and metrics tracking.
    """
    
    def __init__(self, config_path: str = "./config/config.yaml"):
        """
        Initialize the ETL pipeline.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        self.metrics = PipelineMetrics()
        
        # Setup logging
        log_config = self.config.get('pipeline', {})
        log_file = log_config.get('log_file')
        log_level = log_config.get('log_level', 'INFO')
        
        # Ensure log directory exists
        if log_file:
            ensure_directory(Path(log_file).parent)
        
        setup_logging(log_level, log_file)
        
        # Initialize components
        self.extractor = DataExtractor(self.config)
        self.transformer = DataTransformer(self.config)
        self.loader = DataLoader(self.config)
        
        logger.info("ETL Pipeline initialized")
    
    def run(self, source_type: Optional[str] = None) -> bool:
        """
        Run the complete ETL pipeline.
        
        Args:
            source_type: Optional specific source to process ('csv', 'json', 'api')
                        If None, processes all configured sources
        
        Returns:
            True if successful, False otherwise
        """
        self.metrics.start()
        logger.info("=" * 80)
        logger.info("Starting ETL Pipeline")
        logger.info("=" * 80)
        
        try:
            # EXTRACT
            logger.info("Stage 1: EXTRACT")
            logger.info("-" * 80)
            
            if source_type:
                # Process single source
                df_raw = self._extract_single_source(source_type)
                if df_raw is None:
                    return False
                data_sources = {source_type: df_raw}
            else:
                # Process all sources
                data_sources = self.extractor.extract_all()
                
                if not data_sources:
                    logger.error("No data extracted from any source")
                    return False
            
            # Track extraction metrics
            total_extracted = sum(len(df) for df in data_sources.values())
            self.metrics.records_extracted = total_extracted
            logger.info(f"Total records extracted: {total_extracted}")
            
            # TRANSFORM
            logger.info("\nStage 2: TRANSFORM")
            logger.info("-" * 80)
            
            transformed_data = {}
            for source, df in data_sources.items():
                logger.info(f"Transforming data from {source}...")
                
                try:
                    df_transformed = self.transformer.transform(df)
                    transformed_data[source] = df_transformed
                    
                    # Log data profile
                    profile = self.transformer.get_data_profile(df_transformed)
                    logger.info(f"  Rows: {profile['row_count']}, Columns: {profile['column_count']}")
                    
                except Exception as e:
                    logger.error(f"Transformation failed for {source}: {str(e)}")
                    self.metrics.add_error(f"Transform error ({source}): {str(e)}")
                    
                    # Check error handling strategy
                    error_handling = self.config['pipeline'].get('error_handling', 'rollback')
                    if error_handling == 'rollback':
                        raise
                    elif error_handling == 'skip':
                        logger.warning(f"Skipping {source} due to error")
                        continue
            
            if not transformed_data:
                logger.error("No data successfully transformed")
                return False
            
            # Track transformation metrics
            total_transformed = sum(len(df) for df in transformed_data.values())
            self.metrics.records_transformed = total_transformed
            logger.info(f"Total records transformed: {total_transformed}")
            
            # LOAD
            logger.info("\nStage 3: LOAD")
            logger.info("-" * 80)
            
            total_loaded = 0
            for source, df in transformed_data.items():
                logger.info(f"Loading data from {source}...")
                
                try:
                    # Determine table name
                    table_name = self.config['output'].get('table_name', 'orders')
                    if len(transformed_data) > 1:
                        # If multiple sources, append source to table name
                        table_name = f"{table_name}_{source}"
                    
                    records_loaded = self.loader.load(df, table_name)
                    total_loaded += records_loaded
                    
                    logger.info(f"  Loaded {records_loaded} records to {table_name}")
                    
                except Exception as e:
                    logger.error(f"Load failed for {source}: {str(e)}")
                    self.metrics.add_error(f"Load error ({source}): {str(e)}")
                    
                    # Check error handling strategy
                    error_handling = self.config['pipeline'].get('error_handling', 'rollback')
                    if error_handling == 'rollback':
                        raise
            
            self.metrics.records_loaded = total_loaded
            logger.info(f"Total records loaded: {total_loaded}")
            
            # SUCCESS
            self.metrics.end()
            self._log_summary()
            
            return True
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            self.metrics.add_error(f"Pipeline error: {str(e)}")
            self.metrics.end()
            self._log_summary()
            
            return False
        
        finally:
            # Cleanup
            self.loader.close()
    
    def _extract_single_source(self, source_type: str):
        """Extract from a single source type."""
        try:
            if source_type == 'csv':
                return self.extractor.extract_csv()
            elif source_type == 'json':
                return self.extractor.extract_json()
            elif source_type == 'api':
                return self.extractor.extract_api()
            else:
                logger.error(f"Unknown source type: {source_type}")
                return None
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            self.metrics.add_error(f"Extract error: {str(e)}")
            return None
    
    def _log_summary(self):
        """Log pipeline execution summary."""
        summary = self.metrics.get_summary()
        
        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE EXECUTION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Duration: {summary['duration_seconds']:.2f} seconds")
        logger.info(f"Records Extracted: {summary['records_extracted']}")
        logger.info(f"Records Transformed: {summary['records_transformed']}")
        logger.info(f"Records Loaded: {summary['records_loaded']}")
        logger.info(f"Success Rate: {summary['success_rate']:.2f}%")
        logger.info(f"Errors: {summary['error_count']}")
        
        if summary['errors']:
            logger.info("\nErrors encountered:")
            for error in summary['errors']:
                logger.info(f"  [{error['timestamp']}] {error['error']}")
        
        logger.info("=" * 80)
    
    def validate_config(self) -> bool:
        """
        Validate pipeline configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        logger.info("Validating configuration...")
        
        required_sections = ['database', 'sources', 'transformations', 'pipeline', 'output']
        
        for section in required_sections:
            if section not in self.config:
                logger.error(f"Missing required configuration section: {section}")
                return False
        
        logger.info("Configuration validation passed")
        return True


def main():
    """Main entry point for the pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run ETL Pipeline')
    parser.add_argument(
        '--config',
        type=str,
        default='./config/config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--source',
        type=str,
        choices=['csv', 'json', 'api'],
        help='Process only this source type'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Only validate configuration, do not run pipeline'
    )
    
    args = parser.parse_args()
    
    # Create pipeline
    pipeline = ETLPipeline(args.config)
    
    # Validate configuration
    if not pipeline.validate_config():
        logger.error("Configuration validation failed")
        sys.exit(1)
    
    if args.validate:
        logger.info("Configuration is valid")
        sys.exit(0)
    
    # Run pipeline
    success = pipeline.run(args.source)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()