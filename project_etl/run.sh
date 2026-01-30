#!/bin/bash

# ETL Pipeline Quick Start Script
# This script sets up and runs the ETL pipeline

echo "========================================="
echo "ETL Pipeline Quick Start"
echo "========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 found${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create necessary directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p data/raw data/processed logs
echo -e "${GREEN}✓ Directories created${NC}"

# Check if sample data exists
if [ ! -f "data/raw/orders.csv" ]; then
    echo -e "${RED}Warning: Sample data not found in data/raw/${NC}"
    echo "Please add your data files to data/raw/ directory"
fi

# Run the pipeline
echo ""
echo "========================================="
echo "Running ETL Pipeline"
echo "========================================="
python -m src.pipeline

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}Pipeline completed successfully!${NC}"
    echo -e "${GREEN}=========================================${NC}"
else
    echo ""
    echo -e "${RED}=========================================${NC}"
    echo -e "${RED}Pipeline failed. Check logs for details.${NC}"
    echo -e "${RED}=========================================${NC}"
    exit 1
fi

# Show results
echo ""
echo "Results:"
echo "- Database: data/processed/pipeline.db"
echo "- Logs: logs/pipeline.log"
echo ""
echo "To query the database:"
echo "  sqlite3 data/processed/pipeline.db"
echo ""
echo "To run tests:"
echo "  pytest tests/ -v"
