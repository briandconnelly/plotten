# Default: list available recipes
default:
    @just --list

# Run linting and format checks
lint:
    uv run ruff check src/ tests/
    uv run ruff format --check src/ tests/

# Auto-fix lint and format issues
fix:
    uv run ruff check --fix src/ tests/
    uv run ruff format src/ tests/

# Run type checker
types:
    uv run ty check src/

# Run tests (stop on first failure)
test *args:
    uv run pytest tests/ -x {{args}}

# Run tests with coverage report
cov *args:
    uv run pytest tests/ --cov --cov-report=term-missing {{args}}

# Run full verification: lint + types + tests
check:
    uv run ruff check src/ tests/
    uv run ruff format --check src/ tests/
    uv run ty check src/
    uv run pytest tests/ -x

# Build documentation locally
docs:
    uv run python docs/generate_images.py
    uv run mkdocs build

# Serve documentation locally with live reload
docs-serve:
    uv run mkdocs serve

# Install dev dependencies and pre-commit hooks
setup:
    uv sync
    uv run prek install
