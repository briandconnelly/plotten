## Project Conventions

- When writing markdown, use one sentence per line for easy diffs
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
- Test coverage threshold is 95%
- `rg` and `fd` are available as alternatives for `grep` and `find`, respectively

## Dependencies

- **narwhals** for dataframe abstraction — never import pandas in `src/plotten/`. pandas is fine in tests and examples.
- **scipy** is optional — guard imports and degrade gracefully

## Error handling

- Never raise `ValueError` or `TypeError` — use the appropriate `PlottenError` subclass from `_validation.py`
- Use `plotten_warn()` instead of `warnings.warn()` for warnings that should become errors in strict mode
- All public functions that can raise should document errors in a `Raises` docstring section

## Rendering

- Create figures via `_layout.py:create_figure()` using `constrained_layout` — never use `tight_layout()` or manual `subplots_adjust()`

## Verification

Run before presenting work as complete:

```bash
uvx ruff check src/ tests/ && uvx ruff format --check src/ tests/ && uv run pytest tests/ -x
```

Pre-commit hooks run ruff, ty (type checker), and other checks — fix issues rather than skipping hooks.
