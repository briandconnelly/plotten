# Accessibility

Tools for auditing plot accessibility before publication or sharing.

`accessibility_report()` checks for data-visualization-specific accessibility issues:

1. **Colorblind safety** — simulates deuteranopia, protanopia, and tritanopia to detect colors that become indistinguishable under color vision deficiency.
2. **Redundant encoding** — flags when color is the only channel distinguishing groups, leaving colorblind readers with no fallback.
3. **Palette size** — warns when a discrete palette exceeds 8 levels, which are difficult to distinguish even with full color vision.
4. **Contrast ratios** — checks that text elements have sufficient contrast against their background.
5. **Font sizes** — flags text elements below a minimum readable size.
6. **Legend presence** — warns when a legend is suppressed but mapped aesthetics are present.
7. **Descriptive text** — suggests adding a title for use as alt-text when images are embedded in documents or web pages.

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
