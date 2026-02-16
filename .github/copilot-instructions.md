# AutoNova ERP - Copilot Instructions

## Project Overview

AutoNova ERP is a Flask-based Enterprise Resource Planning (ERP) system. This is a Python web application built with the Flask framework.

**Repository Size:** Small (currently minimal structure)
**Primary Language:** Python
**Framework:** Flask 2.0.1
**Type:** Web Application (ERP System)

## Technology Stack

- **Backend Framework:** Flask 2.0.1
- **Database ORM:** Flask-SQLAlchemy 2.5.1
- **Database Migration:** Flask-Migrate 3.1.0
- **Configuration:** python-dotenv 0.17.1 (for environment variable management)

## Project Structure

```
autonova-erp/
├── .github/              # GitHub configuration and workflows
├── backend/              # Backend application code
│   └── requirements.txt  # Python dependencies
├── .gitignore           # Git ignore patterns
└── README.md            # Project documentation
```

**Key Files:**
- `backend/requirements.txt` - Python package dependencies for the Flask application
- `.gitignore` - Excludes `__pycache__/`, `*.pyc`, `venv/`, `node_modules/`, `.env`

## Development Environment Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)
- Virtual environment tool (venv or virtualenv)

### Initial Setup Steps

1. **Create a virtual environment** (ALWAYS do this first):
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   - On Linux/macOS: `source venv/bin/activate`
   - On Windows: `venv\Scripts\activate`

3. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

## Build and Run Instructions

### Installing Dependencies
**ALWAYS run this before building or testing:**
```bash
pip install -r backend/requirements.txt
```

### Running the Application
Currently, no main application entry point is defined. When creating Flask applications:
- The main application file is typically named `app.py` or `main.py`
- Run with: `python app.py` or `flask run`
- Flask applications typically run on port 5000 by default

### Database Operations
Since Flask-Migrate is included:
- Initialize migrations: `flask db init`
- Create migration: `flask db migrate -m "description"`
- Apply migrations: `flask db upgrade`

## Testing

Currently, no test framework is configured. When adding tests:
- Common Python testing frameworks include pytest, unittest
- Tests are typically placed in a `tests/` directory
- Run tests with: `pytest` or `python -m pytest`

## Linting and Code Quality

No linting tools are currently configured. Common Python linters include:
- `pylint` - General purpose linter
- `flake8` - Style guide enforcement
- `black` - Code formatter
- `mypy` - Type checking

## Important Notes for Coding Agents

1. **Virtual Environment:** ALWAYS ensure the virtual environment is activated before running pip install or any Python commands.

2. **Environment Variables:** The project uses python-dotenv, so check for `.env` file requirements. The `.env` file should NEVER be committed (it's in .gitignore).

3. **Dependencies:** When adding new dependencies:
   - Add them to `backend/requirements.txt`
   - Run `pip install -r backend/requirements.txt` to install them
   - Check for security vulnerabilities before adding

4. **Python Version:** Ensure compatibility with Python 3.7+ when writing code.

5. **Flask Best Practices:**
   - Follow Flask application factory pattern for better modularity
   - Use blueprints for organizing routes
   - Keep configuration in separate files
   - Use Flask-SQLAlchemy for database operations

6. **Git Ignore Patterns:** Never commit:
   - `__pycache__/` directories
   - `*.pyc` files
   - `venv/` or virtual environment directories
   - `node_modules/` directories
   - `.env` files (sensitive configuration)

7. **Code Changes:** When making changes:
   - Follow PEP 8 Python style guidelines
   - Use meaningful variable and function names
   - Add docstrings to functions and classes
   - Keep functions small and focused

## CI/CD and Validation

Currently, no GitHub Actions workflows or CI/CD pipelines are configured. When they are added:
- Check `.github/workflows/` for workflow definitions
- Run the same validation steps locally before pushing

## Common Issues and Workarounds

1. **Import Errors:** Ensure all dependencies are installed and virtual environment is activated.
2. **Database Connection:** Check that database configuration is properly set in environment variables.
3. **Port Conflicts:** Flask default port is 5000. If blocked, specify a different port: `flask run --port=8000`

## Trust These Instructions

These instructions are comprehensive and validated. Only search for additional information if:
- The instructions are incomplete for your specific task
- You encounter an error not covered here
- The instructions appear to be outdated or incorrect
