# ETL Pipeline Usage Guide

## Quick Start

### 1. Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Pipeline
```bash
# Run full pipeline
python -m src.pipeline

# Run with specific source
python -m src.pipeline --source csv

# Validate configuration only
python -m src.pipeline --validate
```

### 3. Run Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html

# Run specific test file
pytest tests/test_extract.py -v
```

## Configuration

Edit `config/config.yaml` to customize:

### Database Settings
```yaml
database:
  type: sqlite  # or postgresql
  path: ./data/processed/pipeline.db
```

### Data Sources
```yaml
sources:
  csv:
    path: ./data/raw/orders.csv
  json:
    path: ./data/raw/customers.json
```

### Transformation Rules
```yaml
transformations:
  required_columns:
    - order_id
    - customer_name
  data_types:
    quantity: integer
    price: float
```

## Common Tasks

### Adding a New Data Source

1. **Update Configuration** (`config/config.yaml`):
```yaml
sources:
  excel:
    path: ./data/raw/sales.xlsx
    sheet_name: Sheet1
```

2. **Add Extraction Method** (`src/extract.py`):
```python
def extract_excel(self, source_config=None):
    config = source_config or self.sources.get('excel', {})
    df = pd.read_excel(
        config['path'],
        sheet_name=config.get('sheet_name', 0)
    )
    return df
```

### Adding Custom Transformations

Edit `src/transform.py` in the `_enrich_data` method:

```python
def _enrich_data(self, df: pd.DataFrame) -> pd.DataFrame:
    # Add your custom logic
    df['discount'] = df['total_amount'] * 0.1
    df['order_month'] = pd.to_datetime(df['order_date']).dt.month
    return df
```

### Changing Database

**For PostgreSQL:**

1. Update `config/config.yaml`:
```yaml
database:
  type: postgresql
  host: localhost
  port: 5432
  database: etl_db
  user: postgres
  password: ${DB_PASSWORD}  # Set DB_PASSWORD environment variable
```

2. Install PostgreSQL driver:
```bash
pip install psycopg2-binary
```

## Pipeline Components

### Extract (`src/extract.py`)
- Supports CSV, JSON, and API sources
- Implements retry logic for API calls
- Handles missing files gracefully

### Transform (`src/transform.py`)
- Data cleaning (whitespace, standardization)
- Type conversion (string → int/float/datetime)
- Validation (required columns, data quality)
- Enrichment (calculated fields, timestamps)

### Load (`src/load.py`)
- Database connection management
- Transaction handling
- Index creation
- Multiple write modes (append/replace/fail)

## Debugging

### Enable Debug Logging
Update `config/config.yaml`:
```yaml
pipeline:
  log_level: DEBUG
```

### View Logs
Logs are written to both console and file:
```bash
tail -f logs/pipeline.log
```

### Run Individual Stages
```python
from utils import load_config
from extract import extract_data
from transform import transform_data
from load import load_data

config = load_config()

# Extract only
df = extract_data(config, 'csv')

# Transform only
df_transformed = transform_data(df, config)

# Load only
load_data(df_transformed, config)
```

## Performance Tips

### Large Files
For large CSV files, use chunking:
```python
# In extract.py
df = pd.read_csv(file_path, chunksize=10000)
for chunk in df:
    process_chunk(chunk)
```

### Database Performance
- Create indexes on frequently queried columns
- Use batch inserts (already implemented)
- Consider partitioning for very large tables

### Memory Usage
- Process data in chunks
- Delete intermediate DataFrames
- Use appropriate data types (Int64 vs int64)

## Error Handling

The pipeline supports three error handling modes (in `config.yaml`):

```yaml
pipeline:
  error_handling: rollback  # Options: rollback, skip, continue
```

- **rollback**: Stop and rollback on any error (default)
- **skip**: Skip the failing source and continue
- **continue**: Log error but attempt to continue

## Testing

### Test Structure
```
tests/
├── test_extract.py   # Extraction tests
├── test_transform.py # Transformation tests
└── test_load.py      # Loading tests
```

### Writing New Tests
```python
import pytest

def test_my_feature():
    # Arrange
    data = create_test_data()
    
    # Act
    result = my_function(data)
    
    # Assert
    assert result is not None
```

### Test Coverage
```bash
# Generate coverage report
pytest tests/ --cov=src --cov-report=html

# View report
open htmlcov/index.html
```

## Deployment

### Production Checklist
- [ ] Update database credentials (use environment variables)
- [ ] Set log level to INFO or WARNING
- [ ] Configure appropriate error handling
- [ ] Set up monitoring/alerting
- [ ] Document any custom transformations
- [ ] Run full test suite
- [ ] Backup existing data

### Environment Variables
```bash
export DB_PASSWORD="your_password"
export DB_HOST="production.database.com"
export LOG_LEVEL="INFO"
```

### Running in Production
```bash
# With error handling
python -m src.pipeline 2>&1 | tee pipeline.log

# As a cron job (daily at 2 AM)
0 2 * * * cd /path/to/project && /path/to/venv/bin/python -m src.pipeline
```

## Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Make sure you're in the project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Database Connection Errors:**
- Check database credentials
- Verify database is running
- Test connection manually

**Data Quality Issues:**
- Check transformation logs
- Review data profile output
- Adjust quality thresholds in config

**Memory Errors:**
- Process data in smaller chunks
- Increase available memory
- Optimize data types

## Next Steps

1. **Extend the Pipeline:**
   - Add more data sources (APIs, databases)
   - Implement data deduplication
   - Add data lineage tracking

2. **Improve Monitoring:**
   - Add metrics dashboard
   - Set up email alerts
   - Implement data quality reports

3. **Optimize Performance:**
   - Add parallel processing
   - Implement incremental loads
   - Use connection pooling

4. **Production Readiness:**
   - Set up CI/CD pipeline
   - Add integration tests
   - Document all configurations
