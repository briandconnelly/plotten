# Milestone: Documentation Excellence

## Goal

Make plotten's documentation best-in-class for a plotting library.
Every function gets a visual example, guides cover key workflows, and the gallery serves as a browsable cookbook.

## Image generation

- Create `docs/generate_images.py` — a standalone script that produces all example PNGs
- Output to `docs/images/generated/` (gitignored, built in CI)
- Organized into subdirectories: `geoms/`, `scales/`, `stats/`, `positions/`, `coords/`, `themes/`, `facets/`, `recipes/`, `composition/`, `gallery/`
- Every public `geom_*`, `scale_*`, `stat_*`, `coord_*`, `position_*`, and `theme_*` gets at least one image
- CI workflow runs the script before `mkdocs build`

## Reference pages

- Each reference page (geoms.md, scales.md, etc.) includes rendered example images inline alongside the mkdocstrings API docs
- Images referenced as `![](../images/generated/geoms/point.png)` etc.
- One image minimum per function; complex functions (e.g. `geom_smooth`, `facet_grid`) may have multiple showing different options

## Gallery

- Cookbook-style page: categorized image grid with collapsible code blocks
- Sections: Geoms, Scales, Statistics, Facets & Coordinates, Themes, Composition, Recipes
- Each entry: image + collapsible `??? example "Code"` block with the full script
- Replace current gallery.md which only uses the 6 tracked hero images

## Guides (4 new pages)

### Bindable aesthetics (`docs/guides/bindable-aesthetics.md`)
- How `aes()` mappings work
- Which aesthetics each geom supports (table or per-geom list)
- Set vs map: `aes(color="class")` vs `geom_point(color="red")`
- Computed aesthetics: `after_stat()`, `after_scale()`, `stage()`

### Theming deep dive (`docs/guides/theming.md`)
- Built-in theme showcase (image of each theme applied to the same plot)
- `theme()` element system: `element_text`, `element_line`, `element_rect`, `element_blank`
- Creating a custom theme
- Google Fonts via `register_google_font()`
- `theme_set()` / `theme_get()` / `theme_update()` for global defaults

### ggplot2 migration (`docs/guides/ggplot2-migration.md`)
- Self-contained side-by-side R and Python code blocks
- Cover: ggplot, aes, geoms, scales, facets, themes, ggsave
- Differences and gotchas (e.g. `colour` alias, `coord_flip` vs pandas-native)
- What's supported, what's not yet

### Polars/pandas interop (`docs/guides/dataframes.md`)
- How narwhals provides DataFrame abstraction
- Tips for polars users, tips for pandas users
- Lazy vs eager evaluation
- Performance considerations

## README cleanup

- Keep: hero image, tagline, feature bullet list, one quick example, install instructions
- Remove: Dependencies table, detailed feature sections with images, long code examples
- Add: prominent link to docs site
- Result: concise landing page for GitHub/PyPI that points to the website

## Remove `examples/` directory

- Delete `examples/` directory (scripts and standalone images)
- Move `docs/generate_readme_images.py` logic into `docs/generate_images.py`
- Remove `examples/output/` from `.gitignore` (no longer needed)
- The `docs/images/` directory (hero.png etc.) remains tracked for README and landing page

## CI changes

- Update `.github/workflows/docs.yml`:
  - Add step: `uv run python docs/generate_images.py` before `mkdocs build`
  - Needs `scipy` extra for smooth/ellipse geoms
  - Consider caching generated images by script hash to speed up builds

## Navigation update

```yaml
nav:
  - Home: index.md
  - Getting Started:
      - Installation: getting-started/installation.md
      - Quick Start: getting-started/quickstart.md
  - Gallery: gallery.md
  - Guides:
      - Bindable Aesthetics: guides/bindable-aesthetics.md
      - Theming: guides/theming.md
      - ggplot2 Migration: guides/ggplot2-migration.md
      - DataFrames: guides/dataframes.md
  - Reference:
      - Core: reference/core.md
      - Geoms: reference/geoms.md
      - Scales: reference/scales.md
      - Stats: reference/stats.md
      - Positions: reference/positions.md
      - Coords: reference/coords.md
      - Facets: reference/facets.md
      - Themes: reference/themes.md
      - Datasets: reference/datasets.md
      - Recipes: reference/recipes.md
      - Composition: reference/composition.md
      - Accessibility: reference/accessibility.md
  - Changelog: changelog.md
```

## Suggested work order

1. `docs/generate_images.py` — scaffolding + a few geoms to prove the pattern
2. Reference page images — flesh out generate_images.py for all functions, update reference .md files
3. Gallery rewrite — cookbook-style with code blocks
4. Guides — one at a time (aesthetics, theming, migration, dataframes)
5. README cleanup + remove `examples/`
6. CI workflow update + final verification

## Verification

```bash
uv sync --extra docs --extra scipy
uv run python docs/generate_images.py
uv run mkdocs build --strict
uv run mkdocs serve  # visual review
```
