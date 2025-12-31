from enum import Enum, unique


@unique
class BeatStudioNoteName(Enum):
    CRASH = "CRASH"
    CRASH2 = "CRASH2"
    RIDE = "RIDE"
    HI_HAT = "HI-HAT"
    OPEN_HIHAT = "OPEN-HIHAT"
    KICK = "KICK"
    SNARE = "SNARE"
    HI_TOM = "HI-TOM"
    MED_TOM = "MED-TOM"
    LOW_TOM = "LOW-TOM"
