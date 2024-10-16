from enum import Enum, auto

class D_LENS_STATUS(Enum):
    SUCCESS = auto()
    NOT_FOUND = auto()
    FOUND_MORE_ONE = auto()
    
class INK_L_STATUS(Enum):
    SUCCESS = auto()
    NOT_FOUND = auto()
    