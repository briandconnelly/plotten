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

**scipy** enables smooth geoms, confidence ellipses, and correlation p-values:

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
