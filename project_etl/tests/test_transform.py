"""
Tests for the transformation module.

Tests data cleaning, validation, and enrichment.
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from transform import DataTransformer, transform_data
from project_etl.etl.utils import load_config


@pytest.fixture
def config():
    """Load test configuration."""
    return load_config('./config/config.yaml')


@pytest.fixture
def transformer(config):
    """Create DataTransformer instance."""
    return DataTransformer(config)


@pytest.fixture
def sample_data():
    """Create sample DataFrame for testing."""
    return pd.DataFrame({
        'order_id': ['ORD-001', 'ORD-002', 'ORD-003'],
        'customer_name': [' John Doe ', 'Jane Smith', 'Bob Johnson'],
        'product': ['Widget A', 'Widget B', 'Widget A'],
        'quantity': ['5', '3', '2'],
        'price': ['29.99', '49.99', '29.99'],
        'order_date': ['2024-01-15', '2024-01-16', '2024-01-17']
    })


@pytest.fixture
def dirty_data():
    """Create dirty DataFrame for testing cleaning."""
    return pd.DataFrame({
        'order_id': ['ORD-001', 'ORD-002', 'ORD-001'],  # Duplicate
        'customer_name': [' John Doe ', '  Jane Smith  ', 'Bob Johnson'],  # Whitespace
        'product': ['Widget A', None, 'Widget B'],  # Null
        'quantity': ['5', 'invalid', '2'],  # Invalid data
        'price': ['29.99', '49.99', '29.99'],
        'order_date': ['2024-01-15', 'invalid-date', '2024-01-17']  # Invalid date
    })


class TestDataCleaning:
    """Tests for data cleaning operations."""
    
    def test_strip_whitespace(self, transformer, dirty_data):
        """Test that whitespace is stripped from string columns."""
        df_clean = transformer._clean_data(dirty_data)
        
        # Check that whitespace is removed
        assert df_clean['customer_name'].iloc[0] == 'John Doe'
        assert df_clean['customer_name'].iloc[1] == 'Jane Smith'
    
    def test_column_name_standardization(self, transformer):
        """Test that column names are standardized."""
        df = pd.DataFrame({
            'Order ID': [1, 2],
            'Customer Name': ['John', 'Jane']
        })
        
        df_clean = transformer._clean_data(df)
        
        assert 'order_id' in df_clean.columns
        assert 'customer_name' in df_clean.columns


class TestDataTypeConversion:
    """Tests for data type conversion."""
    
    def test_integer_conversion(self, transformer, sample_data):
        """Test conversion of quantity to integer."""
        df_transformed = transformer._convert_data_types(sample_data)
        
        assert pd.api.types.is_integer_dtype(df_transformed['quantity'])
    
    def test_float_conversion(self, transformer, sample_data):
        """Test conversion of price to float."""
        df_transformed = transformer._convert_data_types(sample_data)
        
        assert pd.api.types.is_float_dtype(df_transformed['price'])
    
    def test_datetime_conversion(self, transformer, sample_data):
        """Test conversion of dates to datetime."""
        df_transformed = transformer._standardize_dates(sample_data)
        
        assert pd.api.types.is_datetime64_any_dtype(df_transformed['order_date'])


class TestDuplicateHandling:
    """Tests for duplicate record handling."""
    
    def test_remove_duplicates(self, transformer, dirty_data):
        """Test that duplicates are removed."""
        initial_count = len(dirty_data)
        df_clean = transformer._remove_duplicates(dirty_data)
        
        assert len(df_clean) < initial_count
        assert df_clean['order_id'].duplicated().sum() == 0


class TestDataValidation:
    """Tests for data validation."""
    
    def test_required_columns_present(self, transformer, sample_data):
        """Test that required columns exist."""
        # Should not raise an error
        df_validated = transformer._validate_required_columns(sample_data)
        assert df_validated is not None
    
    def test_required_columns_missing(self, transformer):
        """Test error when required columns are missing."""
        df = pd.DataFrame({
            'order_id': [1, 2],
            'customer_name': ['John', 'Jane']
            # Missing other required columns
        })
        
        with pytest.raises(ValueError, match="Missing required columns"):
            transformer._validate_required_columns(df)


class TestDataEnrichment:
    """Tests for data enrichment."""
    
    def test_add_processed_timestamp(self, transformer, sample_data):
        """Test that processed_at timestamp is added."""
        df_enriched = transformer._enrich_data(sample_data)
        
        assert 'processed_at' in df_enriched.columns
        assert pd.api.types.is_datetime64_any_dtype(df_enriched['processed_at'])
    
    def test_calculate_total_amount(self, transformer):
        """Test calculation of total_amount."""
        df = pd.DataFrame({
            'order_id': ['ORD-001'],
            'customer_name': ['John Doe'],
            'product': ['Widget A'],
            'quantity': [5],
            'price': [29.99],
            'order_date': ['2024-01-15']
        })
        
        df_enriched = transformer._enrich_data(df)
        
        assert 'total_amount' in df_enriched.columns
        expected_total = 5 * 29.99
        assert abs(df_enriched['total_amount'].iloc[0] - expected_total) < 0.01


class TestTransformPipeline:
    """Tests for complete transformation pipeline."""
    
    def test_full_transform(self, transformer, sample_data):
        """Test complete transformation pipeline."""
        df_transformed = transformer.transform(sample_data)
        
        # Check that data is not empty
        assert not df_transformed.empty
        
        # Check that enrichment occurred
        assert 'processed_at' in df_transformed.columns
        assert 'total_amount' in df_transformed.columns
    
    def test_transform_with_dirty_data(self, transformer, dirty_data):
        """Test transformation with dirty data."""
        # Should handle dirty data gracefully
        df_transformed = transformer.transform(dirty_data)
        
        # Should have removed duplicates
        assert len(df_transformed) < len(dirty_data)


class TestDataProfile:
    """Tests for data profiling."""
    
    def test_get_data_profile(self, transformer, sample_data):
        """Test data profile generation."""
        profile = transformer.get_data_profile(sample_data)
        
        assert 'row_count' in profile
        assert 'column_count' in profile
        assert 'columns' in profile
        assert 'data_types' in profile
        assert 'null_counts' in profile
        
        assert profile['row_count'] == len(sample_data)
        assert profile['column_count'] == len(sample_data.columns)


class TestConvenienceFunction:
    """Tests for convenience functions."""
    
    def test_transform_data_function(self, config, sample_data):
        """Test transform_data convenience function."""
        df_transformed = transform_data(sample_data, config)
        
        assert isinstance(df_transformed, pd.DataFrame)
        assert not df_transformed.empty


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
