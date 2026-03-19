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


class SmoothMethod(StrEnum):
    OLS = "ols"
    LOESS = "loess"
    MOVING_AVERAGE = "moving_average"


class SizeUnit(StrEnum):
    INCHES = "in"
    CM = "cm"
    MM = "mm"
    PX = "px"
