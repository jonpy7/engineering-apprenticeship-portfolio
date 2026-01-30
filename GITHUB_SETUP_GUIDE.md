# GitHub Setup Guide - Engineering Apprenticeship Portfolio

## Step 1: Create the GitHub Repository

1. Go to GitHub (https://github.com)
2. Click the **"+"** button in the top right
3. Select **"New repository"**

### Repository Settings:
- **Repository name**: `engineering-apprenticeship-portfolio`
- **Visibility**: ✅ Public
- **Initialize with README**: ❌ No (we have our own)
- **Add .gitignore**: None
- **License**: MIT

Click **"Create repository"**

## Step 2: Upload Your Files

### Option A: Using GitHub Web Interface (Easier for Beginners)

1. In your new repository, click **"uploading an existing file"**
2. Drag and drop the entire `engineering-apprenticeship-portfolio` folder
3. Or click **"choose your files"** and select all files
4. Write a commit message: "Initial commit - ETL pipeline project"
5. Click **"Commit changes"**

### Option B: Using Git Command Line (Recommended)

```bash
# Navigate to your project folder
cd path/to/engineering-apprenticeship-portfolio

# Initialize git repository
git init

# Add all files
git add .

# Make initial commit
git commit -m "Initial commit - ETL pipeline project"

# Add GitHub as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/jonpy7/engineering-apprenticeship-portfolio.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Verify Your Repository

Your repository should have this structure:

```
engineering-apprenticeship-portfolio/
├── README.md                    # Portfolio overview
├── LICENSE                      # MIT License
├── PROJECT_STRUCTURE.md         # Structure documentation
└── project_etl/                 # ETL project folder
    ├── README.md
    ├── USAGE.md
    ├── requirements.txt
    ├── setup.py
    ├── Makefile
    ├── run.sh
    ├── .gitignore
    ├── config/
    │   └── config.yaml
    ├── src/
    │   ├── __init__.py
    │   ├── utils.py
    │   ├── extract.py
    │   ├── transform.py
    │   ├── load.py
    │   └── pipeline.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_extract.py
    │   ├── test_transform.py
    │   └── test_load.py
    └── data/
        └── raw/
            ├── orders.csv
            └── customers.json
```

## Step 4: Enhance Your Repository

### Add Topics (Tags)
1. Click **"About"** settings (gear icon) on the right side
2. Add topics:
   - `data-engineering`
   - `etl-pipeline`
   - `python`
   - `apprenticeship`
   - `portfolio`
   - `sql`
   - `data-pipeline`

### Add Description
In the same "About" section:
- **Description**: "Data engineering portfolio showcasing ETL pipelines, testing, and production-ready code"
- **Website**: Your LinkedIn URL

## Step 5: Create Additional Folders (For Future Projects)

```bash
# In your repository root
mkdir project_streaming
mkdir project_api
mkdir project_algorithms

# Create placeholder READMEs
echo "# Event Stream Simulator" > project_streaming/README.md
echo "# API Integration Project" > project_api/README.md
echo "# Algorithms & Data Structures" > project_algorithms/README.md

# Commit and push
git add .
git commit -m "Add placeholder folders for future projects"
git push
```

## Step 6: Best Practices Going Forward

### Making Changes
```bash
# Make your changes to files
# ...

# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add: feature description"

# Push to GitHub
git push
```

### Commit Message Guidelines
- `Add:` for new features
- `Fix:` for bug fixes
- `Update:` for improvements
- `Docs:` for documentation changes
- `Test:` for test additions

Example:
```bash
git commit -m "Add: PostgreSQL support to load.py"
git commit -m "Fix: handle missing columns in transform"
git commit -m "Docs: update usage guide with examples"
```

### Branch Protection (Optional but Professional)
1. Go to **Settings** → **Branches**
2. Add branch protection rule for `main`
3. Require pull request reviews (for collaboration)

## Step 7: Share Your Portfolio

### On Your Resume
```
GitHub: github.com/jonpy7/engineering-apprenticeship-portfolio
```

### On LinkedIn
1. Add to **Featured** section
2. Link in your profile summary
3. Post about your project:
   ```
   🚀 Excited to share my data engineering portfolio!
   
   I've built a production-ready ETL pipeline demonstrating:
   ✅ Modular design
   ✅ Data validation
   ✅ Comprehensive testing
   ✅ Error handling
   ✅ Documentation
   
   Check it out: [GitHub link]
   
   #DataEngineering #Python #ETL #ApprenticeshipReady
   ```

## Step 8: Maintain Your Portfolio

### Weekly Updates
- Add new projects to separate folders
- Improve existing code based on feedback
- Update README with new skills learned

### Quality Checks Before Commits
```bash
# Run tests
pytest tests/ -v

# Format code
black src/ tests/

# Check for issues
flake8 src/ tests/

# All good? Commit!
git add .
git commit -m "Your message"
git push
```

## Troubleshooting

### "Repository already exists"
- You created it on GitHub first
- Solution: Use `git clone` instead of `git init`

```bash
git clone https://github.com/jonpy7/engineering-apprenticeship-portfolio.git
cd engineering-apprenticeship-portfolio
# Add your files
git add .
git commit -m "Initial commit"
git push
```

### Large Files Error
GitHub limits files to 100MB:
- Don't commit database files (`.db`)
- Don't commit large datasets
- `.gitignore` already handles this

### Authentication Issues
GitHub removed password authentication:
- Use Personal Access Token (PAT)
- Or set up SSH keys

**To create a PAT:**
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select scopes: `repo`
4. Copy token and use as password

## Next Steps

1. ✅ Create repository
2. ✅ Upload code
3. ✅ Add topics and description
4. ✅ Share on LinkedIn
5. 🔄 Build next project (streaming/API/algorithms)
6. 🔄 Get feedback and iterate
7. 🔄 Apply to apprenticeships

## Resources

- **GitHub Docs**: https://docs.github.com
- **Git Tutorial**: https://www.atlassian.com/git/tutorials
- **Markdown Guide**: https://www.markdownguide.org

## Questions?

If you encounter issues:
1. Check GitHub documentation
2. Search Stack Overflow
3. Ask in developer communities
4. Review Git error messages carefully

Good luck with your apprenticeship applications! 🚀
