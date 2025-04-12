# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Run Commands
- Run development server: `python run.py`
- Initialize database: `flask db init`
- Create migration: `flask db migrate -m "migration message"`
- Apply migrations: `flask db upgrade`
- Run tests: `pytest`
- Run a single test: `pytest tests/path_to_test.py::TestClass::test_function`
- Run with test coverage: `pytest --cov=app`

## Code Style Guidelines
- Follow PEP 8 style guidelines
- Sort imports: standard library → third-party → local app imports
- Group imports with a single blank line between groups
- Use SQLAlchemy models with type annotations
- Snake_case for variables and functions, PascalCase for classes
- Error handling: Use try/except with specific exceptions
- Blueprints for modular organization
- Use f-strings for string formatting
- Factory pattern for application creation
- Include docstrings for functions and classes