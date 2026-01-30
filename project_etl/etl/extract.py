"""
Data Extraction Module

Handles extraction of data from various sources including CSV, JSON, and APIs.
Implements retry logic, error handling, and data validation.
"""

import pandas as pd
import requests
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from time import sleep


logger = logging.getLogger("etl_pipeline.extract")


class DataExtractor:
    """
    Base class for data extraction from various sources.
    
    Supports CSV, JSON files, and REST APIs with configurable retry logic
    and error handling.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the DataExtractor.
        
        Args:
            config: Configuration dictionary containing source settings
        """
        self.config = config
        self.sources = config.get('sources', {})
    
    def extract_csv(self, source_config: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Extract data from CSV file.
        
        Args:
            source_config: Optional configuration override
            
        Returns:
            DataFrame containing extracted data
            
        Raises:
            FileNotFoundError: If CSV file doesn't exist
            pd.errors.ParserError: If CSV is malformed
        """
        config = source_config or self.sources.get('csv', {})
        file_path = config.get('path')
        
        if not file_path:
            raise ValueError("CSV file path not configured")
        
        logger.info(f"Extracting data from CSV: {file_path}")
        
        if not Path(file_path).exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        try:
            df = pd.read_csv(
                file_path,
                encoding=config.get('encoding', 'utf-8'),
                delimiter=config.get('delimiter', ',')
            )
            
            logger.info(f"Successfully extracted {len(df)} records from CSV")
            return df
            
        except Exception as e:
            logger.error(f"Error extracting CSV: {str(e)}")
            raise
    
    def extract_json(self, source_config: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Extract data from JSON file.
        
        Args:
            source_config: Optional configuration override
            
        Returns:
            DataFrame containing extracted data
            
        Raises:
            FileNotFoundError: If JSON file doesn't exist
            json.JSONDecodeError: If JSON is malformed
        """
        config = source_config or self.sources.get('json', {})
        file_path = config.get('path')
        
        if not file_path:
            raise ValueError("JSON file path not configured")
        
        logger.info(f"Extracting data from JSON: {file_path}")
        
        if not Path(file_path).exists():
            raise FileNotFoundError(f"JSON file not found: {file_path}")
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                # Check if it's a dict of lists or a single record
                if all(isinstance(v, list) for v in data.values()):
                    df = pd.DataFrame(data)
                else:
                    df = pd.DataFrame([data])
            else:
                raise ValueError("Unsupported JSON structure")
            
            logger.info(f"Successfully extracted {len(df)} records from JSON")
            return df
            
        except Exception as e:
            logger.error(f"Error extracting JSON: {str(e)}")
            raise
    
    def extract_api(
        self, 
        endpoint: str = None,
        params: Optional[Dict[str, Any]] = None,
        source_config: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        Extract data from REST API with retry logic.
        
        Args:
            endpoint: API endpoint to call (appended to base_url)
            params: Query parameters for the API call
            source_config: Optional configuration override
            
        Returns:
            DataFrame containing extracted data
            
        Raises:
            requests.exceptions.RequestException: If API call fails after retries
        """
        config = source_config or self.sources.get('api', {})
        base_url = config.get('base_url')
        endpoint = endpoint or config.get('endpoint', '')
        timeout = config.get('timeout', 30)
        retry_attempts = config.get('retry_attempts', 3)
        
        if not base_url:
            raise ValueError("API base_url not configured")
        
        url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        logger.info(f"Extracting data from API: {url}")
        
        # Retry logic
        for attempt in range(retry_attempts):
            try:
                response = requests.get(
                    url,
                    params=params,
                    timeout=timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Convert to DataFrame
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                elif isinstance(data, dict):
                    # Check for common API response patterns
                    if 'data' in data:
                        df = pd.DataFrame(data['data'])
                    elif 'results' in data:
                        df = pd.DataFrame(data['results'])
                    else:
                        df = pd.DataFrame([data])
                else:
                    raise ValueError("Unsupported API response structure")
                
                logger.info(f"Successfully extracted {len(df)} records from API")
                return df
                
            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"API call attempt {attempt + 1}/{retry_attempts} failed: {str(e)}"
                )
                
                if attempt < retry_attempts - 1:
                    sleep_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"Retrying in {sleep_time} seconds...")
                    sleep(sleep_time)
                else:
                    logger.error(f"API call failed after {retry_attempts} attempts")
                    raise
    
    def extract_all(self) -> Dict[str, pd.DataFrame]:
        """
        Extract data from all configured sources.
        
        Returns:
            Dictionary mapping source names to DataFrames
        """
        results = {}
        
        if 'csv' in self.sources:
            try:
                results['csv'] = self.extract_csv()
            except Exception as e:
                logger.error(f"Failed to extract CSV: {str(e)}")
        
        if 'json' in self.sources:
            try:
                results['json'] = self.extract_json()
            except Exception as e:
                logger.error(f"Failed to extract JSON: {str(e)}")
        
        if 'api' in self.sources:
            try:
                results['api'] = self.extract_api()
            except Exception as e:
                logger.error(f"Failed to extract from API: {str(e)}")
        
        logger.info(f"Extraction complete. Sources extracted: {list(results.keys())}")
        return results


def extract_data(config: Dict[str, Any], source_type: str = 'csv') -> pd.DataFrame:
    """
    Convenience function to extract data from a specific source.
    
    Args:
        config: Pipeline configuration
        source_type: Type of source ('csv', 'json', 'api')
        
    Returns:
        DataFrame containing extracted data
    """
    extractor = DataExtractor(config)
    
    if source_type == 'csv':
        return extractor.extract_csv()
    elif source_type == 'json':
        return extractor.extract_json()
    elif source_type == 'api':
        return extractor.extract_api()
    else:
        raise ValueError(f"Unsupported source type: {source_type}")


if __name__ == "__main__":
    # Example usage for testing
    from project_etl.etl.utils import load_config, setup_logging
    
    config = load_config()
    setup_logging(config['pipeline']['log_level'])
    
    extractor = DataExtractor(config)
    data = extractor.extract_all()
    
    for source, df in data.items():
        print(f"\n{source.upper()} Data:")
        print(df.head())
