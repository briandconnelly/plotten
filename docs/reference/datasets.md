# Datasets

Built-in datasets for examples and testing.

::: plotten.load_dataset

## Available datasets

| Dataset | Description | Rows | Source |
|---------|-------------|------|--------|
| `diamonds` | Prices and attributes of ~54,000 diamonds | 53,940 | ggplot2 |
| `mtcars` | Motor Trend car road tests (1974) | 32 | R datasets |
| `iris` | Edgar Anderson's iris measurements | 150 | R datasets |
| `faithful` | Old Faithful geyser eruption data | 272 | R datasets |
| `tips` | Restaurant tipping data | 244 | reshape2 |
| `mpg` | Fuel economy data (1999-2008) | 234 | ggplot2 |
| `penguins` | Palmer Archipelago penguin measurements | 344 | palmerpenguins |

```python
from plotten.datasets import load_dataset

mpg = load_dataset("mpg")
diamonds = load_dataset("diamonds")
```
