# Project Structure

```
engineering-apprenticeship-portfolio/
│
├── README.md                          # Main portfolio README
├── LICENSE                            # MIT License
│
└── project_etl/                       # ETL Pipeline Project
    │
    ├── README.md                      # Project-specific README
    ├── USAGE.md                       # Detailed usage guide
    ├── requirements.txt               # Python dependencies
    ├── setup.py                       # Package setup
    ├── Makefile                       # Common commands
    ├── run.sh                         # Quick start script
    ├── .gitignore                     # Git ignore rules
    │
    ├── config/                        # Configuration files
    │   └── config.yaml               # Pipeline configuration
    │
    ├── src/                          # Source code
    │   ├── __init__.py              # Package initialization
    │   ├── utils.py                 # Utility functions
    │   ├── extract.py               # Data extraction
    │   ├── transform.py             # Data transformation
    │   ├── load.py                  # Data loading
    │   └── pipeline.py              # Pipeline orchestration
    │
    ├── tests/                        # Test suite
    │   ├── __init__.py
    │   ├── test_extract.py          # Extraction tests
    │   ├── test_transform.py        # Transformation tests
    │   └── test_load.py             # Loading tests
    │
    ├── data/                         # Data directory
    │   ├── raw/                     # Raw input data
    │   │   ├── orders.csv          # Sample CSV data
    │   │   └── customers.json      # Sample JSON data
    │   └── processed/               # Processed output
    │       └── pipeline.db         # SQLite database (generated)
    │
    └── logs/                         # Log files
        └── pipeline.log             # Pipeline logs (generated)
```

## File Descriptions

### Root Level
- **README.md**: Portfolio overview and project links
- **LICENSE**: MIT license for open source sharing

### Project Level (project_etl/)
- **README.md**: Comprehensive project documentation
- **USAGE.md**: Detailed usage instructions and examples
- **requirements.txt**: Python package dependencies
- **setup.py**: Python package setup configuration
- **Makefile**: Shortcuts for common commands
- **run.sh**: Quick start script to run the pipeline
- **.gitignore**: Files to exclude from version control

### Configuration (config/)
- **config.yaml**: Central configuration for all pipeline settings

### Source Code (src/)
- **__init__.py**: Package marker
- **utils.py**: Shared utilities (logging, config, metrics)
- **extract.py**: Data extraction from CSV, JSON, APIs
- **transform.py**: Data cleaning, validation, enrichment
- **load.py**: Database loading and management
- **pipeline.py**: Main orchestrator coordinating all stages

### Tests (tests/)
- **test_extract.py**: Tests for extraction logic
- **test_transform.py**: Tests for transformation logic
- **test_load.py**: Tests for loading logic

### Data (data/)
- **raw/**: Source data files (CSV, JSON)
- **processed/**: Output database and processed files

### Logs (logs/)
- **pipeline.log**: Execution logs with timestamps

## Key Features

### Modular Design
Each component (Extract, Transform, Load) is:
- Independently testable
- Loosely coupled
- Easily extensible

### Configuration-Driven
All settings in YAML:
- Data sources
- Transformation rules
- Database connections
- Quality thresholds

### Production-Ready
Includes:
- Comprehensive error handling
- Structured logging
- Metrics tracking
- Test coverage
- Documentation

### Developer-Friendly
Provides:
- Sample data for testing
- Quick start script
- Makefile for common tasks
- Detailed usage guide
- Type hints in code

## Getting Started

1. **Clone the repository**
2. **Navigate to project_etl/**
3. **Run the quick start script:**
   ```bash
   ./run.sh
   ```

Or follow manual setup in USAGE.md
