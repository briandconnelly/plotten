from enum import StrEnum


class LegendPosition(StrEnum):
    RIGHT = "right"
    LEFT = "left"
    TOP = "top"
    BOTTOM = "bottom"
    NONE = "none"


class FacetScales(StrEnum):
    FIXED = "fixed"
    FREE = "free"
    FREE_X = "free_x"
    FREE_Y = "free_y"


class AnnotationType(StrEnum):
    TEXT = "text"
    RECT = "rect"
    SEGMENT = "segment"
    CURVE = "curve"
    BRACKET = "bracket"


class AnnotationCoord(StrEnum):
    DATA = "data"
    NPC = "npc"


class SmoothMethod(StrEnum):
    OLS = "ols"
    LOESS = "loess"
    MOVING_AVERAGE = "moving_average"
    POLY = "poly"


class SizeUnit(StrEnum):
    INCHES = "in"
    CM = "cm"
    MM = "mm"
    PX = "px"


class StripPosition(StrEnum):
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"


class Direction(StrEnum):
    HORIZONTAL = "h"
    VERTICAL = "v"


class TagLevel(StrEnum):
    UPPERCASE = "A"
    LOWERCASE = "a"
    NUMERIC = "1"
    ROMAN = "i"


class ViridisOption(StrEnum):
    VIRIDIS = "viridis"
    MAGMA = "magma"
    INFERNO = "inferno"
    PLASMA = "plasma"
    CIVIDIS = "cividis"


class Transform(StrEnum):
    LOG10 = "log10"
    SQRT = "sqrt"
    REVERSE = "reverse"


class PolarAxis(StrEnum):
    X = "x"
    Y = "y"


class GuideType(StrEnum):
    NONE = "none"
    LEGEND = "legend"
    COLORBAR = "colorbar"
