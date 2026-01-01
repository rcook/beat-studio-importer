from enum import Enum, unique


# Keys and names derived from default midi-mapping.properties
@unique
class BeatStudioNoteName(Enum):
    # Key 55 "crash_cymbal"
    CRASH = "CRASH"
    # Key 52 "crash_cymbal_2"
    CRASH2 = "CRASH2"
    # Key 59 "ride_cymbal"
    RIDE = "RIDE"
    # Key 26 "hi-hat_closed"
    HI_HAT = "HI-HAT"
    # Key 26 "hi-hat_open"
    OPEN_HIHAT = "OPEN-HIHAT"
    # Key 36 "kick_drum"
    KICK = "KICK"
    # Key 38 "snare_drum"
    SNARE = "SNARE"
    # Key 48 "high_tom"
    HI_TOM = "HI-TOM"
    # Key 45 "mid_tom"
    MED_TOM = "MED-TOM"
    # Key 43 "low_tom"
    LOW_TOM = "LOW-TOM"
