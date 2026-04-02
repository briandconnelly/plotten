# Installation

## Install with pip

```bash
pip install plotten
```

## Install with uv

```bash
uv add plotten
```

## Optional dependencies

plotten's core works without scipy, but some features require it:

- `geom_smooth(method="loess")` — LOESS smoothing
- `stat_ellipse()` — confidence ellipses (chi-squared quantiles)
- `stat_cor()` — correlation p-values (exact computation; a pure-Python fallback is used when scipy is absent)
- `stat_density()` — Gaussian KDE (falls back to a histogram-based estimate without scipy)

Install with the `scipy` extra:

=== "pip"

    ```bash
    pip install "plotten[scipy]"
    ```

=== "uv"

    ```bash
    uv add "plotten[scipy]"
    ```

## Requirements

- Python >= 3.13
- matplotlib >= 3.8
- numpy >= 1.24
- narwhals >= 1.0

## Development setup

To contribute or run plotten from source:

```bash
git clone https://github.com/briandconnelly/plotten.git
cd plotten
just setup   # installs dev dependencies and pre-commit hooks
```

Run the full verification suite before submitting changes:

```bash
just check   # lint + type check + tests
```

See the [justfile](https://github.com/briandconnelly/plotten/blob/main/justfile) for all available recipes.
