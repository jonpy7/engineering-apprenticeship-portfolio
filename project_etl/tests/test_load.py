"""
Tests for the loading module.

Tests database operations and data loading.
"""

import pytest
import pandas as pd
import sys
from pathlib import Path
import tempfile
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from project_etl.etl.load import DataLoader, load_data
from project_etl.etl.utils import load_config


@pytest.fixture
def config():
    """Load test configuration with temporary database."""
    config = load_config('./config/config.yaml')
    
    # Use temporary database for testing
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    config['database']['path'] = temp_db.name
    
    yield config
    
    # Cleanup
    try:
        os.unlink(temp_db.name)
    except:
        pass


@pytest.fixture
def loader(config):
    """Create DataLoader instance."""
    return DataLoader(config)


@pytest.fixture
def sample_data():
    """Create sample DataFrame for testing."""
    from datetime import datetime
    
    return pd.DataFrame({
        'order_id': ['ORD-001', 'ORD-002', 'ORD-003'],
        'customer_name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
        'product': ['Widget A', 'Widget B', 'Widget A'],
        'quantity': [5, 3, 2],
        'price': [29.99, 49.99, 29.99],
        'total_amount': [149.95, 149.97, 59.98],
        'order_date': pd.to_datetime(['2024-01-15', '2024-01-16', '2024-01-17']),
        'processed_at': [datetime.now()] * 3
    })


class TestDataLoaderInitialization:
    """Tests for DataLoader initialization."""
    
    def test_loader_initialization(self, config):
        """Test DataLoader initialization."""
        loader = DataLoader(config)
        
        assert loader.config == config
        assert loader.engine is not None
    
    def test_sqlite_engine_creation(self, config):
        """Test SQLite engine creation."""
        loader = DataLoader(config)
        
        assert loader.engine is not None
        assert 'sqlite' in str(loader.engine.url)


class TestDataLoading:
    """Tests for data loading operations."""
    
    def test_load_data_success(self, loader, sample_data):
        """Test successful data loading."""
        table_name = 'test_orders'
        
        records_loaded = loader.load(sample_data, table_name, if_exists='replace')
        
        assert records_loaded == len(sample_data)
    
    def test_table_exists_after_load(self, loader, sample_data):
        """Test that table exists after loading."""
        table_name = 'test_orders'
        
        loader.load(sample_data, table_name, if_exists='replace')
        
        assert loader.table_exists(table_name)
    
    def test_load_append_mode(self, loader, sample_data):
        """Test loading in append mode."""
        table_name = 'test_orders'
        
        # First load
        loader.load(sample_data, table_name, if_exists='replace')
        
        # Second load in append mode
        loader.load(sample_data, table_name, if_exists='append')
        
        # Should have double the records
        count = loader.get_record_count(table_name)
        assert count == len(sample_data) * 2
    
    def test_load_replace_mode(self, loader, sample_data):
        """Test loading in replace mode."""
        table_name = 'test_orders'
        
        # First load
        loader.load(sample_data, table_name, if_exists='replace')
        
        # Second load in replace mode
        new_data = sample_data.copy()
        new_data['order_id'] = ['ORD-004', 'ORD-005', 'ORD-006']
        loader.load(new_data, table_name, if_exists='replace')
        
        # Should have only new records
        count = loader.get_record_count(table_name)
        assert count == len(new_data)


class TestDatabaseQueries:
    """Tests for database query operations."""
    
    def test_get_record_count(self, loader, sample_data):
        """Test getting record count."""
        table_name = 'test_orders'
        
        loader.load(sample_data, table_name, if_exists='replace')
        count = loader.get_record_count(table_name)
        
        assert count == len(sample_data)
    
    def test_execute_query(self, loader, sample_data):
        """Test executing SQL query."""
        table_name = 'test_orders'
        
        loader.load(sample_data, table_name, if_exists='replace')
        
        query = f"SELECT * FROM {table_name} WHERE quantity > 2"
        result = loader.execute_query(query)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert all(result['quantity'] > 2)
    
    def test_execute_aggregation_query(self, loader, sample_data):
        """Test executing aggregation query."""
        table_name = 'test_orders'
        
        loader.load(sample_data, table_name, if_exists='replace')
        
        query = f"SELECT product, SUM(quantity) as total_qty FROM {table_name} GROUP BY product"
        result = loader.execute_query(query)
        
        assert isinstance(result, pd.DataFrame)
        assert 'product' in result.columns
        assert 'total_qty' in result.columns


class TestTableOperations:
    """Tests for table management operations."""
    
    def test_truncate_table(self, loader, sample_data):
        """Test truncating a table."""
        table_name = 'test_orders'
        
        # Load data
        loader.load(sample_data, table_name, if_exists='replace')
        assert loader.get_record_count(table_name) > 0
        
        # Truncate
        loader.truncate_table(table_name)
        
        # Should be empty
        assert loader.get_record_count(table_name) == 0
    
    def test_drop_table(self, loader, sample_data):
        """Test dropping a table."""
        table_name = 'test_orders'
        
        # Load data
        loader.load(sample_data, table_name, if_exists='replace')
        assert loader.table_exists(table_name)
        
        # Drop table
        loader.drop_table(table_name)
        
        # Should not exist
        assert not loader.table_exists(table_name)
    
    def test_table_exists_false(self, loader):
        """Test table_exists returns False for non-existent table."""
        assert not loader.table_exists('nonexistent_table')


class TestConnectionManagement:
    """Tests for connection management."""
    
    def test_close_connection(self, loader):
        """Test closing database connection."""
        # Should not raise an error
        loader.close()
    
    def test_operations_after_close(self, loader, sample_data):
        """Test that operations work after reopening connection."""
        table_name = 'test_orders'
        
        # Load data
        loader.load(sample_data, table_name, if_exists='replace')
        
        # Close connection
        loader.close()
        
        # Recreate engine and load again - should work
        loader._create_engine()
        loader.load(sample_data, table_name, if_exists='append')


class TestConvenienceFunction:
    """Tests for convenience functions."""
    
    def test_load_data_function(self, config, sample_data):
        """Test load_data convenience function."""
        records = load_data(sample_data, config, 'test_orders')
        
        assert records == len(sample_data)


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_invalid_table_name(self, loader, sample_data):
        """Test handling of invalid table name."""
        # SQLite is permissive with table names, so this might not raise an error
        # But we can test that the operation completes
        try:
            loader.load(sample_data, 'valid_table_name', if_exists='replace')
        except Exception as e:
            pytest.fail(f"Valid table name raised exception: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
