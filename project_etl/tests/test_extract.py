"""
Tests for the extraction module.

Tests data extraction from CSV, JSON, and API sources.
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from extract import DataExtractor, extract_data
from project_etl.etl.utils import load_config


@pytest.fixture
def config():
    """Load test configuration."""
    return load_config('./config/config.yaml')


@pytest.fixture
def extractor(config):
    """Create DataExtractor instance."""
    return DataExtractor(config)


class TestCSVExtraction:
    """Tests for CSV extraction."""
    
    def test_extract_csv_success(self, extractor):
        """Test successful CSV extraction."""
        df = extractor.extract_csv()
        
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert len(df) > 0
    
    def test_extract_csv_columns(self, extractor):
        """Test that CSV has expected columns."""
        df = extractor.extract_csv()
        
        expected_columns = ['order_id', 'customer_name', 'product', 'quantity', 'price', 'order_date']
        assert all(col in df.columns for col in expected_columns)
    
    def test_extract_csv_file_not_found(self, config):
        """Test handling of missing CSV file."""
        config['sources']['csv']['path'] = './nonexistent.csv'
        extractor = DataExtractor(config)
        
        with pytest.raises(FileNotFoundError):
            extractor.extract_csv()
    
    def test_extract_csv_data_types(self, extractor):
        """Test that data types are reasonable."""
        df = extractor.extract_csv()
        
        # Check that we have some object and numeric types
        assert df['customer_name'].dtype == 'object'
        assert df['quantity'].dtype in ['int64', 'object']


class TestJSONExtraction:
    """Tests for JSON extraction."""
    
    def test_extract_json_success(self, extractor):
        """Test successful JSON extraction."""
        df = extractor.extract_json()
        
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert len(df) > 0
    
    def test_extract_json_columns(self, extractor):
        """Test that JSON has expected columns."""
        df = extractor.extract_json()
        
        expected_columns = ['order_id', 'customer_name', 'product', 'quantity', 'price', 'order_date']
        assert all(col in df.columns for col in expected_columns)
    
    def test_extract_json_file_not_found(self, config):
        """Test handling of missing JSON file."""
        config['sources']['json']['path'] = './nonexistent.json'
        extractor = DataExtractor(config)
        
        with pytest.raises(FileNotFoundError):
            extractor.extract_json()


class TestDataExtractor:
    """Tests for DataExtractor class."""
    
    def test_extractor_initialization(self, config):
        """Test DataExtractor initialization."""
        extractor = DataExtractor(config)
        
        assert extractor.config == config
        assert extractor.sources == config['sources']
    
    def test_extract_all_sources(self, extractor):
        """Test extracting from all sources."""
        results = extractor.extract_all()
        
        assert isinstance(results, dict)
        assert 'csv' in results or 'json' in results
        
        # Check that all results are DataFrames
        for source, df in results.items():
            assert isinstance(df, pd.DataFrame)


class TestConvenienceFunction:
    """Tests for convenience functions."""
    
    def test_extract_data_csv(self, config):
        """Test extract_data function with CSV."""
        df = extract_data(config, 'csv')
        
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
    
    def test_extract_data_json(self, config):
        """Test extract_data function with JSON."""
        df = extract_data(config, 'json')
        
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
    
    def test_extract_data_invalid_source(self, config):
        """Test extract_data with invalid source type."""
        with pytest.raises(ValueError):
            extract_data(config, 'invalid_source')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
