"""
Data Loading Module

Handles loading transformed data into the target database.
Implements transaction management, error handling, and index creation.
"""

import pandas as pd
import logging
from typing import Dict, Any, Optional
from sqlalchemy import (
    create_engine, 
    MetaData, 
    Table, 
    Column, 
    Integer, 
    String, 
    Float, 
    DateTime,
    inspect,
    text
)
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError


logger = logging.getLogger("etl_pipeline.load")


class DataLoader:
    """
    Handles loading data into the target database.
    
    Supports SQLite and PostgreSQL with transaction management,
    index creation, and configurable write modes.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the DataLoader.
        
        Args:
            config: Configuration dictionary containing database settings
        """
        self.config = config
        self.db_config = config.get('database', {})
        self.output_config = config.get('output', {})
        self.engine = self._create_engine()
    
    def _create_engine(self) -> Engine:
        """
        Create SQLAlchemy engine based on configuration.
        
        Returns:
            SQLAlchemy Engine instance
        """
        db_type = self.db_config.get('type', 'sqlite')
        
        if db_type == 'sqlite':
            db_path = self.db_config.get('path', './data/processed/pipeline.db')
            connection_string = f"sqlite:///{db_path}"
            logger.info(f"Creating SQLite connection: {db_path}")
            
        elif db_type == 'postgresql':
            host = self.db_config.get('host', 'localhost')
            port = self.db_config.get('port', 5432)
            database = self.db_config.get('database')
            user = self.db_config.get('user')
            password = self.db_config.get('password')
            
            connection_string = (
                f"postgresql://{user}:{password}@{host}:{port}/{database}"
            )
            logger.info(f"Creating PostgreSQL connection: {host}:{port}/{database}")
            
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        engine = create_engine(connection_string, echo=False)
        return engine
    
    def load(
        self, 
        df: pd.DataFrame, 
        table_name: Optional[str] = None,
        if_exists: Optional[str] = None
    ) -> int:
        """
        Load DataFrame into the database.
        
        Args:
            df: DataFrame to load
            table_name: Target table name (uses config if not provided)
            if_exists: How to handle existing table ('append', 'replace', 'fail')
            
        Returns:
            Number of records loaded
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        table_name = table_name or self.output_config.get('table_name', 'orders')
        if_exists = if_exists or self.output_config.get('write_mode', 'append')
        
        logger.info(
            f"Loading {len(df)} records to table '{table_name}' (mode: {if_exists})"
        )
        
        try:
            # Load data
            df.to_sql(
                name=table_name,
                con=self.engine,
                if_exists=if_exists,
                index=False,
                method='multi',
                chunksize=1000
            )
            
            records_loaded = len(df)
            logger.info(f"Successfully loaded {records_loaded} records")
            
            # Create indexes if configured
            if self.output_config.get('create_indexes', True):
                self._create_indexes(table_name, df)
            
            return records_loaded
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to load data: {str(e)}")
            raise
    
    def _create_indexes(self, table_name: str, df: pd.DataFrame) -> None:
        """
        Create indexes on the loaded table.
        
        Args:
            table_name: Table name
            df: DataFrame (used to infer index columns)
        """
        logger.debug(f"Creating indexes for table '{table_name}'")
        
        try:
            with self.engine.connect() as conn:
                # Create index on timestamp column if it exists
                if 'processed_at' in df.columns:
                    index_sql = f"""
                        CREATE INDEX IF NOT EXISTS idx_{table_name}_processed_at 
                        ON {table_name} (processed_at)
                    """
                    conn.execute(text(index_sql))
                    conn.commit()
                    logger.debug(f"Created index on processed_at")
                
                # Create index on order_id if it exists (common primary key)
                if 'order_id' in df.columns:
                    index_sql = f"""
                        CREATE INDEX IF NOT EXISTS idx_{table_name}_order_id 
                        ON {table_name} (order_id)
                    """
                    conn.execute(text(index_sql))
                    conn.commit()
                    logger.debug(f"Created index on order_id")
                    
        except SQLAlchemyError as e:
            logger.warning(f"Failed to create indexes: {str(e)}")
    
    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.
        
        Args:
            table_name: Table name to check
            
        Returns:
            True if table exists, False otherwise
        """
        inspector = inspect(self.engine)
        return table_name in inspector.get_table_names()
    
    def get_record_count(self, table_name: str) -> int:
        """
        Get the number of records in a table.
        
        Args:
            table_name: Table name
            
        Returns:
            Number of records
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text(f"SELECT COUNT(*) FROM {table_name}")
                )
                count = result.scalar()
                return count
        except SQLAlchemyError as e:
            logger.error(f"Failed to count records: {str(e)}")
            return 0
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute a SQL query and return results as DataFrame.
        
        Args:
            query: SQL query to execute
            
        Returns:
            Query results as DataFrame
        """
        logger.debug(f"Executing query: {query}")
        
        try:
            df = pd.read_sql(query, self.engine)
            return df
        except SQLAlchemyError as e:
            logger.error(f"Query failed: {str(e)}")
            raise
    
    def truncate_table(self, table_name: str) -> None:
        """
        Truncate (delete all records from) a table.
        
        Args:
            table_name: Table name to truncate
        """
        logger.warning(f"Truncating table '{table_name}'")
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text(f"DELETE FROM {table_name}"))
                conn.commit()
                logger.info(f"Table '{table_name}' truncated")
        except SQLAlchemyError as e:
            logger.error(f"Failed to truncate table: {str(e)}")
            raise
    
    def drop_table(self, table_name: str) -> None:
        """
        Drop a table from the database.
        
        Args:
            table_name: Table name to drop
        """
        logger.warning(f"Dropping table '{table_name}'")
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
                conn.commit()
                logger.info(f"Table '{table_name}' dropped")
        except SQLAlchemyError as e:
            logger.error(f"Failed to drop table: {str(e)}")
            raise
    
    def close(self) -> None:
        """Close the database connection."""
        if self.engine:
            self.engine.dispose()
            logger.debug("Database connection closed")


def load_data(
    df: pd.DataFrame, 
    config: Dict[str, Any],
    table_name: Optional[str] = None
) -> int:
    """
    Convenience function to load data into the database.
    
    Args:
        df: DataFrame to load
        config: Pipeline configuration
        table_name: Optional table name override
        
    Returns:
        Number of records loaded
    """
    loader = DataLoader(config)
    try:
        records = loader.load(df, table_name)
        return records
    finally:
        loader.close()


if __name__ == "__main__":
    # Example usage for testing
    from project_etl.etl.utils import load_config, setup_logging
    from extract import extract_data
    from transform import transform_data
    
    config = load_config()
    setup_logging(config['pipeline']['log_level'])
    
    # Extract, transform, and load
    df = extract_data(config, 'csv')
    df_transformed = transform_data(df, config)
    
    loader = DataLoader(config)
    
    try:
        # Load data
        records_loaded = loader.load(df_transformed)
        print(f"\nLoaded {records_loaded} records")
        
        # Query the data
        table_name = config['output']['table_name']
        count = loader.get_record_count(table_name)
        print(f"Total records in table: {count}")
        
        # Show sample data
        query = f"SELECT * FROM {table_name} LIMIT 5"
        result = loader.execute_query(query)
        print("\nSample data from database:")
        print(result)
        
    finally:
        loader.close()