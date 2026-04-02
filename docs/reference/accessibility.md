# Accessibility

Tools for auditing plot accessibility before publication or sharing.

`accessibility_report()` runs three checks on a rendered plot:

1. **Colorblind safety** — simulates deuteranopia, protanopia, and tritanopia to detect colors that become indistinguishable under color vision deficiency.
2. **Contrast ratios** — checks that text and foreground elements have sufficient contrast against their background, following WCAG guidelines.
3. **Font sizes** — flags text elements below a minimum readable size.

```python
from plotten import ggplot, aes, geom_point, accessibility_report
from plotten.datasets import load_dataset

mpg = load_dataset("mpg")

p = ggplot(mpg, aes(x="displ", y="hwy", color="class")) + geom_point()
report = accessibility_report(p)

print(report)           # human-readable summary
print(report.passed)    # True if no errors or warnings
```

::: plotten.accessibility_report

::: plotten.AccessibilityReport

## Fonts

Register custom fonts so matplotlib can render them in your plots.
`register_google_font()` downloads and registers a font from Google Fonts.

::: plotten.register_font

::: plotten.register_google_font

::: plotten.available_fonts
