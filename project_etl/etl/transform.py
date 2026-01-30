"""
Data Transformation Module

Handles data cleaning, validation, enrichment, and quality checks.
Implements schema validation, data type conversion, and business logic.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime


logger = logging.getLogger("etl_pipeline.transform")


class DataTransformer:
    """
    Handles transformation and validation of extracted data.
    
    Performs data cleaning, type conversion, validation, and enrichment
    according to configured rules.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the DataTransformer.
        
        Args:
            config: Configuration dictionary containing transformation rules
        """
        self.config = config
        self.transform_config = config.get('transformations', {})
        self.quality_config = config.get('quality', {})
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all transformations to the dataframe.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Transformed DataFrame
        """
        logger.info(f"Starting transformation. Input records: {len(df)}")
        
        # Create a copy to avoid modifying the original
        df = df.copy()
        
        # Apply transformations in order
        df = self._clean_data(df)
        df = self._standardize_dates(df)
        df = self._convert_data_types(df)
        df = self._validate_required_columns(df)
        df = self._remove_duplicates(df)
        df = self._handle_nulls(df)
        df = self._enrich_data(df)
        df = self._validate_quality(df)
        
        logger.info(f"Transformation complete. Output records: {len(df)}")
        return df
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the data by removing whitespace and standardizing values.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        logger.debug("Cleaning data...")
        
        # Strip whitespace from string columns
        string_columns = df.select_dtypes(include=['object']).columns
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].str.strip() if df[col].dtype == 'object' else df[col]
        
        # Standardize column names (lowercase, replace spaces with underscores)
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        return df
    
    def _standardize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert date columns to standard datetime format.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with standardized dates
        """
        date_columns = self.transform_config.get('date_columns', [])
        
        for col in date_columns:
            if col in df.columns:
                logger.debug(f"Converting {col} to datetime")
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except Exception as e:
                    logger.warning(f"Failed to convert {col} to datetime: {str(e)}")
        
        return df
    
    def _convert_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert columns to specified data types.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with converted types
        """
        data_types = self.transform_config.get('data_types', {})
        
        for col, dtype in data_types.items():
            if col in df.columns:
                logger.debug(f"Converting {col} to {dtype}")
                try:
                    if dtype == 'integer':
                        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
                    elif dtype == 'float':
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    elif dtype == 'string':
                        df[col] = df[col].astype(str)
                    elif dtype == 'datetime':
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                except Exception as e:
                    logger.warning(f"Failed to convert {col} to {dtype}: {str(e)}")
        
        return df
    
    def _validate_required_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate that required columns exist and have values.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Validated DataFrame
            
        Raises:
            ValueError: If required columns are missing
        """
        required_columns = self.transform_config.get('required_columns', [])
        
        # Check for missing columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        logger.debug(f"All required columns present: {required_columns}")
        return df
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate records based on configuration.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with duplicates removed
        """
        allow_duplicates = self.quality_config.get('allow_duplicates', False)
        
        if not allow_duplicates:
            initial_count = len(df)
            df = df.drop_duplicates()
            removed_count = initial_count - len(df)
            
            if removed_count > 0:
                logger.info(f"Removed {removed_count} duplicate records")
        
        return df
    
    def _handle_nulls(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle null values according to quality rules.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with nulls handled
        """
        max_null_pct = self.quality_config.get('max_null_percentage', 0.05)
        
        for col in df.columns:
            null_pct = df[col].isna().sum() / len(df)
            
            if null_pct > max_null_pct:
                logger.warning(
                    f"Column {col} has {null_pct*100:.2f}% null values "
                    f"(threshold: {max_null_pct*100:.2f}%)"
                )
        
        return df
    
    def _enrich_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add derived columns and enrich the data.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Enriched DataFrame
        """
        logger.debug("Enriching data...")
        
        # Add processing timestamp
        df['processed_at'] = datetime.now()
        
        # Calculate total_amount if quantity and price exist
        if 'quantity' in df.columns and 'price' in df.columns:
            df['total_amount'] = df['quantity'] * df['price']
            logger.debug("Added total_amount column")
        
        # Add any other business logic transformations here
        
        return df
    
    def _validate_quality(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Perform final quality validation on transformed data.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Validated DataFrame
            
        Raises:
            ValueError: If data quality checks fail
        """
        validate_schema = self.quality_config.get('validate_schema', True)
        
        if validate_schema:
            # Check for completely empty DataFrame
            if df.empty:
                raise ValueError("DataFrame is empty after transformation")
            
            # Check for required columns again (they might have been dropped)
            required_columns = self.transform_config.get('required_columns', [])
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Required columns missing after transformation: {missing_columns}")
            
            logger.info("Data quality validation passed")
        
        return df
    
    def get_data_profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate a data profile with statistics and quality metrics.
        
        Args:
            df: DataFrame to profile
            
        Returns:
            Dictionary containing profile statistics
        """
        profile = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'data_types': df.dtypes.astype(str).to_dict(),
            'null_counts': df.isna().sum().to_dict(),
            'null_percentages': (df.isna().sum() / len(df) * 100).to_dict(),
            'duplicate_count': df.duplicated().sum(),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
        }
        
        return profile


def transform_data(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """
    Convenience function to transform data.
    
    Args:
        df: Input DataFrame
        config: Pipeline configuration
        
    Returns:
        Transformed DataFrame
    """
    transformer = DataTransformer(config)
    return transformer.transform(df)


if __name__ == "__main__":
    # Example usage for testing
    from project_etl.etl.utils import load_config, setup_logging
    from extract import extract_data
    
    config = load_config()
    setup_logging(config['pipeline']['log_level'])
    
    # Extract and transform
    df = extract_data(config, 'csv')
    transformer = DataTransformer(config)
    
    print("\nData Profile (Before):")
    print(transformer.get_data_profile(df))
    
    df_transformed = transformer.transform(df)
    
    print("\nData Profile (After):")
    print(transformer.get_data_profile(df_transformed))
    
    print("\nTransformed Data Sample:")
    print(df_transformed.head())
