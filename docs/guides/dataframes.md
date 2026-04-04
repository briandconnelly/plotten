# Working with DataFrames

plotten works with any DataFrame library supported by [narwhals](https://narwhals-dev.github.io/narwhals/).
You do not need to convert between libraries — just pass your DataFrame directly to `ggplot()`.

## Supported libraries

| Library | Status | Notes |
|---------|--------|-------|
| [Polars](https://pola.rs/) | Supported | Recommended for performance |
| [pandas](https://pandas.pydata.org/) | Supported | Most widely used |
| [cuDF](https://docs.rapids.ai/api/cudf/stable/) | Supported | GPU-accelerated DataFrames |
| [Modin](https://modin.readthedocs.io/) | Supported | Drop-in pandas replacement |
| [PyArrow tables](https://arrow.apache.org/docs/python/) | Supported | Columnar format, zero-copy |

plotten uses narwhals as a DataFrame abstraction layer.
narwhals translates operations into each library's native API, so there is minimal overhead.

## Basic usage

=== "Polars"

    ```python
    import polars as pl
    from plotten import ggplot, aes, geom_point, labs

    df = pl.DataFrame({
        "engine_size": [1.8, 2.0, 2.5, 3.0, 3.5, 4.0],
        "fuel_efficiency": [32, 30, 27, 24, 22, 19],
        "type": ["sedan", "sedan", "suv", "suv", "truck", "truck"],
    })

    (
        ggplot(df, aes(x="engine_size", y="fuel_efficiency", color="type"))
        + geom_point(size=3)
        + labs(x="Engine size (L)", y="Fuel efficiency (mpg)")
    )
    ```

=== "pandas"

    ```python
    import pandas as pd
    from plotten import ggplot, aes, geom_point, labs

    df = pd.DataFrame({
        "engine_size": [1.8, 2.0, 2.5, 3.0, 3.5, 4.0],
        "fuel_efficiency": [32, 30, 27, 24, 22, 19],
        "type": ["sedan", "sedan", "suv", "suv", "truck", "truck"],
    })

    (
        ggplot(df, aes(x="engine_size", y="fuel_efficiency", color="type"))
        + geom_point(size=3)
        + labs(x="Engine size (L)", y="Fuel efficiency (mpg)")
    )
    ```

The code is identical except for the import and DataFrame constructor.
plotten handles the rest.

## Creating data inline for quick plots

For quick experiments, you can create data inline with either library:

=== "Polars"

    ```python
    import polars as pl
    from plotten import ggplot, aes, geom_line

    df = pl.DataFrame({
        "x": list(range(100)),
        "y": [i ** 0.5 for i in range(100)],
    })

    ggplot(df, aes(x="x", y="y")) + geom_line()
    ```

=== "pandas"

    ```python
    import pandas as pd
    from plotten import ggplot, aes, geom_line

    df = pd.DataFrame({
        "x": range(100),
        "y": [i ** 0.5 for i in range(100)],
    })

    ggplot(df, aes(x="x", y="y")) + geom_line()
    ```

## Built-in datasets

plotten includes several built-in datasets for examples and experimentation.
Use `load_dataset()` to load them:

```python
from plotten.datasets import load_dataset

mpg = load_dataset("mpg")
diamonds = load_dataset("diamonds")
penguins = load_dataset("penguins")
```

Available datasets:

| Dataset | Rows | Description |
|---------|------|-------------|
| `"mtcars"` | 32 | Motor Trend car road tests |
| `"iris"` | 150 | Edgar Anderson's iris measurements |
| `"faithful"` | 272 | Old Faithful geyser eruptions |
| `"tips"` | 244 | Restaurant tipping data |
| `"mpg"` | 234 | EPA fuel economy data |
| `"penguins"` | 344 | Palmer Archipelago penguin measurements |
| `"diamonds"` | 53,940 | Diamond prices and attributes |

`load_dataset()` returns a narwhals `DataFrame`.
To get the underlying native frame, call `.to_native()`:

```python
mpg = load_dataset("mpg")

# Get the native polars or pandas frame
native_df = mpg.to_native()
```

!!! tip

    The native backend depends on which library is installed.
    If polars is available, it is preferred.
    Otherwise, pandas is used.

## Tips for Polars users

### Lazy frames are collected automatically

If you pass a Polars `LazyFrame` to `ggplot()`, plotten collects it automatically.
You do not need to call `.collect()` first:

```python
import polars as pl
from plotten import ggplot, aes, geom_point

# LazyFrame works directly
lf = pl.scan_csv("data.csv")
ggplot(lf, aes(x="col_a", y="col_b")) + geom_point()
```

#### Column projection for wide datasets

By default, plotten collects all columns from a lazy frame.
If your dataset has many columns but you only map a few to aesthetics, you can enable `lazy_select` to narrow the frame before collecting.
This enables projection pushdown — the backend skips reading unused columns from disk:

```python
import polars as pl
from plotten import ggplot, aes, geom_point, options

# A wide dataset where we only need two columns
lf = pl.scan_parquet("wide_table.parquet")

with options(lazy_select=True):
    ggplot(lf, aes(x="price", y="volume")) + geom_point()
```

This has no effect on eager frames (the data is already in memory).

!!! note

    `lazy_select` is opt-in because it changes which columns are available
    to stats and other downstream processing.
    Enable it when you know your plot only needs the mapped columns.

### Use column names, not expressions

`aes()` takes string column names, not Polars expressions.
Polars expressions like `pl.col("x") * 2` cannot be used inside `aes()`.

```python
import polars as pl
from plotten import ggplot, aes, geom_point

df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})

# Correct: use string column names
ggplot(df, aes(x="x", y="y")) + geom_point()

# Wrong: Polars expressions are not supported in aes()
# ggplot(df, aes(x=pl.col("x"), y=pl.col("y")))  # raises an error
```

If you need to transform data before plotting, do it before passing the DataFrame:

```python
import polars as pl
from plotten import ggplot, aes, geom_point

df = pl.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})

# Transform first, then plot
df2 = df.with_columns((pl.col("x") * 2).alias("x_doubled"))
ggplot(df2, aes(x="x_doubled", y="y")) + geom_point()
```

### String categories

Polars `Categorical` and `Enum` types work as expected for discrete scales.
No special handling is needed:

```python
import polars as pl
from plotten import ggplot, aes, geom_bar

df = pl.DataFrame({
    "category": pl.Series(["A", "B", "C", "A", "B"]).cast(pl.Categorical),
})

ggplot(df, aes(x="category")) + geom_bar()
```

## Tips for pandas users

### Flatten MultiIndex columns

If your pandas DataFrame has a `MultiIndex` for columns, flatten it before plotting.
plotten expects simple string column names:

```python
import pandas as pd
from plotten import ggplot, aes, geom_point

# After a groupby/agg that creates MultiIndex columns
df = pd.DataFrame({
    ("stats", "mean"): [1, 2, 3],
    ("stats", "std"): [0.1, 0.2, 0.3],
})

# Flatten the MultiIndex
df.columns = ["_".join(col).strip("_") for col in df.columns]

# Now plot with simple column names
ggplot(df, aes(x="stats_mean", y="stats_std")) + geom_point()
```

### Datetime columns

pandas datetime columns work with `scale_x_date()` and `scale_x_datetime()`:

```python
import pandas as pd
from plotten import ggplot, aes, geom_line, scale_x_date

df = pd.DataFrame({
    "date": pd.date_range("2024-01-01", periods=30, freq="D"),
    "value": range(30),
})

(
    ggplot(df, aes(x="date", y="value"))
    + geom_line()
    + scale_x_date()
)
```

### Index columns

plotten reads DataFrame columns, not the index.
If the data you need is in the index, reset it first:

```python
import pandas as pd
from plotten import ggplot, aes, geom_point

df = pd.DataFrame({"y": [1, 4, 9]}, index=[10, 20, 30])
df.index.name = "x"

# Reset the index to make it a regular column
df = df.reset_index()
ggplot(df, aes(x="x", y="y")) + geom_point()
```

## Performance

plotten processes data through narwhals, which dispatches to each library's native operations.
This means:

- **Polars** operations remain Polars-native (Rust-backed, multithreaded)
- **pandas** operations remain pandas-native (NumPy-backed)
- **No data copying** between libraries occurs

For large datasets (100k+ rows), Polars typically offers better performance than pandas for the data processing steps.
The actual rendering is done by matplotlib regardless of the DataFrame backend, so rendering time is the same.

For wide lazy frames, enable `lazy_select` to skip collecting unused columns.
See [Column projection for wide datasets](#column-projection-for-wide-datasets) above.

!!! note

    plotten never converts your DataFrame to a different library.
    If you pass a Polars DataFrame, all internal data operations use Polars.
    If you pass a pandas DataFrame, all internal data operations use pandas.

## Mixing data sources

Each layer can use a different DataFrame.
Pass a `data` argument to the geom to override the plot-level data:

```python
import polars as pl
from plotten import ggplot, aes, geom_point, geom_text

points = pl.DataFrame({"x": [1, 2, 3], "y": [1, 4, 9]})
labels = pl.DataFrame({"x": [2], "y": [4], "label": ["peak"]})

(
    ggplot(points, aes(x="x", y="y"))
    + geom_point(size=3)
    + geom_text(data=labels, aes(label="label"), size=12)
)
```

You can even mix DataFrame libraries across layers — plotten handles each one independently through narwhals.
