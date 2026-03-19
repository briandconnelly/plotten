"""Built-in example datasets for plotten.

All datasets are bundled with the package and require no extra dependencies.

Available datasets
------------------
diamonds (53 940 x 10)
    Prices and attributes of ~54 000 round-cut diamonds.
    Wickham, H. (2016). *ggplot2: Elegant Graphics for Data Analysis.*
    Springer-Verlag New York. License: CC BY 4.0.

faithful (272 x 2)
    Eruption times and waiting times for Old Faithful geyser.
    Hardle, W. (1991). *Smoothing Techniques with Implementation in S.*
    New York: Springer.

iris (150 x 5)
    Measurements of iris flowers from three species.
    Fisher, R.A. (1936). "The Use of Multiple Measurements in Taxonomic
    Problems." *Annals of Eugenics* 7(2): 179-188.
    UCI Machine Learning Repository, DOI: 10.24432/C56C76. License: CC BY 4.0.

mpg (234 x 11)
    Fuel economy data for 234 cars, 1999-2008.
    U.S. Environmental Protection Agency, https://fueleconomy.gov.
    Public domain (U.S. government work).

mtcars (32 x 12)
    Performance data for 32 automobiles from 1974 Motor Trend magazine.
    Henderson, H.V. and Velleman, P.F. (1981). "Building Multiple Regression
    Models Interactively." *Biometrics* 37: 391-411.

penguins (344 x 7)
    Size measurements for three penguin species at Palmer Station, Antarctica.
    Horst, A.M., Hill, A.P., and Gorman, K.B. (2020). palmerpenguins: Palmer
    Archipelago (Antarctica) penguin data. DOI: 10.5281/zenodo.3960218.
    License: CC-0.

tips (244 x 7)
    Restaurant tipping data.
    Bryant, P.G. and Smith, M.A. (1995). *Practical Data Analysis: Case
    Studies in Business Statistics.* Richard D. Irwin Publishing.
"""

from plotten.datasets._loader import load_dataset

__all__ = ["load_dataset"]
