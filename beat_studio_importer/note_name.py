from beat_studio_importer.beat_studio_note_name import BeatStudioNoteName
from enum import Enum, auto, unique


@unique
class NoteName(Enum):
    HI_HAT_CLOSED = auto(), BeatStudioNoteName.HI_HAT
    HIGH_TOM_HIT = auto(), BeatStudioNoteName.HI_TOM
    LEFT_KICK = auto(), BeatStudioNoteName.KICK
    MID_TOM_HIT = auto(), BeatStudioNoteName.MED_TOM
    RIGHT_KICK_HIT = auto(), BeatStudioNoteName.KICK
    SNARE_HIT = auto(), BeatStudioNoteName.SNARE
