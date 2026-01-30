# Quick Reference - ETL Portfolio Project

## 📁 What You Have Here

A complete, production-ready ETL pipeline project with:
- ✅ Full Python source code
- ✅ Comprehensive tests (pytest)
- ✅ Sample data files
- ✅ Configuration management
- ✅ Documentation
- ✅ Quick start script

## 🚀 Quick Start Commands

```bash
# 1. Setup (one time)
cd project_etl
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Run pipeline
python -m src.pipeline

# 3. Run tests
pytest tests/ -v

# 4. Using quick start script (does all of above)
./run.sh
```

## 📂 Key Files

| File | Purpose |
|------|---------|
| `src/pipeline.py` | Main entry point - orchestrates everything |
| `src/extract.py` | Extracts data from CSV, JSON, APIs |
| `src/transform.py` | Cleans, validates, enriches data |
| `src/load.py` | Loads data into SQLite/PostgreSQL |
| `config/config.yaml` | All configuration settings |
| `tests/test_*.py` | Comprehensive test suite |

## 🎯 What This Demonstrates

### Software Engineering Skills
- ✅ Modular design & separation of concerns
- ✅ Error handling & logging
- ✅ Configuration management
- ✅ Unit testing & test coverage
- ✅ Documentation as code

### Data Engineering Skills
- ✅ ETL pattern implementation
- ✅ Data validation & quality checks
- ✅ Database operations (CRUD)
- ✅ Multiple data source handling
- ✅ Transaction management

### Best Practices
- ✅ Type hints for clarity
- ✅ Docstrings for all functions
- ✅ Git-friendly structure
- ✅ Environment variables for secrets
- ✅ Reproducible setup

## 🔧 Common Customizations

### Change Database to PostgreSQL
Edit `config/config.yaml`:
```yaml
database:
  type: postgresql
  host: localhost
  port: 5432
  database: mydb
  user: postgres
  password: ${DB_PASSWORD}
```

### Add New Data Source
1. Add to `config/config.yaml`:
```yaml
sources:
  api:
    base_url: https://api.example.com
    endpoint: /data
```

2. Use in code:
```python
df = extractor.extract_api()
```

### Add Custom Transformation
Edit `src/transform.py`, method `_enrich_data`:
```python
def _enrich_data(self, df):
    # Your custom logic
    df['custom_field'] = df['field1'] * df['field2']
    return df
```

## 📊 Understanding the Data Flow

```
1. EXTRACT
   └─> CSV/JSON/API → DataFrame

2. TRANSFORM
   └─> Clean → Validate → Enrich → DataFrame

3. LOAD
   └─> DataFrame → Database Table
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_extract.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

## 📝 Configuration Explained

### Pipeline Settings
```yaml
pipeline:
  log_level: INFO          # DEBUG, INFO, WARNING, ERROR
  error_handling: rollback # rollback, skip, continue
```

### Quality Rules
```yaml
quality:
  allow_duplicates: false
  max_null_percentage: 0.05  # 5% nulls allowed
  validate_schema: true
```

### Output Settings
```yaml
output:
  table_name: orders
  write_mode: append  # append, replace, fail
```

## 🐛 Troubleshooting

### "ModuleNotFoundError"
```bash
# Make sure you're in the right directory
cd project_etl

# Make sure virtual environment is activated
source venv/bin/activate
```

### "Database locked"
```bash
# Close any SQLite browsers
# Or delete and recreate database
rm data/processed/pipeline.db
python -m src.pipeline
```

### "Config file not found"
```bash
# Run from project root (project_etl/)
# Or specify config path
python -m src.pipeline --config ./config/config.yaml
```

## 💡 Interview Talking Points

When discussing this project:

1. **Design Decisions**
   - Why separate extract/transform/load?
   - How does configuration management help?
   - What makes it production-ready?

2. **Error Handling**
   - Three modes: rollback, skip, continue
   - Comprehensive logging
   - Graceful degradation

3. **Testing Strategy**
   - Unit tests for each component
   - Fixtures for test data
   - Coverage reporting

4. **Extensibility**
   - Easy to add new data sources
   - Pluggable transformations
   - Multiple database support

5. **Real-World Application**
   - Daily batch processing
   - Data warehouse loading
   - API data ingestion

## 📚 Learning Resources

- **Pandas**: https://pandas.pydata.org/docs/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **pytest**: https://docs.pytest.org/
- **ETL Best Practices**: Google "Kimball ETL best practices"

## ✅ Pre-Commit Checklist

Before committing code:
```bash
# 1. Format code
black src/ tests/

# 2. Run tests
pytest tests/ -v

# 3. Check for issues
flake8 src/ tests/

# 4. Update documentation if needed

# 5. Commit with clear message
git add .
git commit -m "Add: clear description of changes"
```

## 🎓 Skills Demonstrated

**For Apprenticeship Applications:**

> "Built a production-ready ETL pipeline in Python demonstrating:
> - Object-oriented design with 5+ classes
> - Comprehensive error handling and logging
> - 95%+ test coverage with pytest
> - Configuration-driven architecture
> - Multiple data source integration (CSV, JSON, APIs)
> - Database operations with SQLAlchemy
> - Clean code principles and documentation"

## 🔗 Quick Links

- Main README: `../README.md`
- Usage Guide: `USAGE.md`
- Project Structure: `../PROJECT_STRUCTURE.md`
- GitHub Setup: `../GITHUB_SETUP_GUIDE.md`

---

**Need Help?**
- Review the USAGE.md for detailed instructions
- Check the code comments and docstrings
- Run tests to see examples of usage
- Refer to GITHUB_SETUP_GUIDE.md for deployment

**Ready to Customize?**
Start by modifying `config/config.yaml` and adding your own data sources!