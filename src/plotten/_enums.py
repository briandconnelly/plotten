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
