# Data Pipeline with Python & SQL

## Overview
A production-ready ETL (Extract, Transform, Load) pipeline that demonstrates best practices in data engineering. This pipeline extracts data from multiple sources (CSV, JSON, API), applies transformations, validates data quality, and loads it into a structured database.

## Technologies
- Python 3.9+
- SQLite (easily adaptable to PostgreSQL/MySQL)
- Pandas for data manipulation
- SQLAlchemy for database interactions
- pytest for testing
- logging for observability

## Problem Statement
Modern data systems require reliable, maintainable pipelines that can:
- Handle multiple data sources and formats
- Transform and clean data consistently
- Validate data quality before loading
- Provide clear error handling and logging
- Be easily tested and extended

## Architecture

```
┌─────────────┐
│   EXTRACT   │  ← CSV, JSON, API sources
└──────┬──────┘
       │
┌──────▼──────┐
│  TRANSFORM  │  ← Clean, validate, enrich
└──────┬──────┘
       │
┌──────▼──────┐
│    LOAD     │  ← SQLite/PostgreSQL
└─────────────┘
```

## Project Structure

```
project_etl/
├── etl/
│   ├── __init__.py
│   ├── extract.py          # Data extraction logic
│   ├── transform.py        # Transformation & validation
│   ├── load.py            # Database loading
│   ├── pipeline.py        # Orchestration
│   └── utils.py           # Shared utilities
├── tests/
│   ├── __init__.py
│   ├── test_extract.py
│   ├── test_transform.py
│   └── test_load.py
├── config/
│   └── config.yaml        # Configuration settings
├── data/
│   ├── raw/              # Sample input data
│   └── processed/        # Transformed data
├── logs/                 # Application logs
├── requirements.txt
├── setup.py
└── README.md
```

## How to Run

### 1. Setup Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Full Pipeline
```bash
python -m src.pipeline
```

### 3. Run Individual Components
```bash
# Extract only
python -m src.extract

# Transform only
python -m src.transform

# Load only
python -m src.load
```

### 4. Run Tests
```bash
pytest tests/ -v
```

## Key Features

### 1. **Modular Design**
- Each stage (Extract, Transform, Load) is independently testable
- Clear separation of concerns
- Easy to swap data sources or destinations

### 2. **Data Validation**
- Schema validation before loading
- Data quality checks (nulls, duplicates, data types)
- Custom validation rules

### 3. **Error Handling**
- Graceful failure recovery
- Detailed error logging
- Transaction rollback on failures

### 4. **Configurability**
- YAML-based configuration
- Environment-specific settings
- Easy to adapt to different data sources

### 5. **Observability**
- Structured logging
- Pipeline metrics tracking
- Clear audit trail

## Sample Data Flow

The pipeline processes customer order data:

**Input (CSV/JSON):**
```json
{
  "order_id": "ORD-001",
  "customer_name": "John Doe",
  "product": "Widget A",
  "quantity": 5,
  "price": 29.99,
  "order_date": "2024-01-15"
}
```

**Transformation:**
- Standardize date formats
- Calculate total_amount (quantity × price)
- Validate required fields
- Remove duplicates
- Enrich with derived fields

**Output (Database):**
```sql
CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(100),
    product VARCHAR(100),
    quantity INTEGER,
    price DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    order_date DATE,
    processed_at TIMESTAMP
);
```

## What I Learned

### Technical Skills
- **Design Patterns**: Implemented the ETL pattern with clear separation of concerns
- **Data Quality**: Built validation frameworks to ensure data integrity
- **Error Handling**: Created robust error handling with proper logging
- **Testing**: Wrote unit tests with fixtures and mocks
- **Database Design**: Designed normalized schemas and efficient queries

### Best Practices
- Configuration management (avoiding hard-coded values)
- Logging for debugging and monitoring
- Documentation as code
- Type hints for better code clarity
- Virtual environments for dependency isolation

### Problem-Solving
- Handling missing or malformed data
- Optimizing memory usage for large datasets
- Designing for extensibility and reusability
- Balancing performance with code readability

## Future Enhancements
- [ ] Add support for PostgreSQL/MySQL
- [ ] Implement incremental loading (change data capture)
- [ ] Add data lineage tracking
- [ ] Create a web dashboard for monitoring
- [ ] Add support for cloud storage (S3, GCS)
- [ ] Implement parallel processing for large datasets
- [ ] Add data quality metrics and reporting

## Contributing
This is a learning project, but suggestions and feedback are welcome! Feel free to open an issue or submit a pull request.

## License
MIT License - Feel free to use this as a learning resource
