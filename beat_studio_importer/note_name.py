from beat_studio_importer.beat_studio_note_name import BeatStudioNoteName
from enum import Enum, auto, unique


# Names derived from General MIDI Drums Level 1 spec
# https://midi.org/general-midi-level-1
# This enum maps GM MIDI drum notes to the equivalent Beat Studio
# note names
@unique
class NoteName(Enum):
    # GM Key 35
    ACOUSTIC_BASS_DRUM = auto(), BeatStudioNoteName.KICK
    # GM Key 36
    BASS_DRUM_1 = auto(), BeatStudioNoteName.KICK
    # GM Key 38
    ACOUSTIC_SNARE = auto(), BeatStudioNoteName.SNARE
    # GM Key 42
    CLOSED_HI_HAT = auto(), BeatStudioNoteName.HI_HAT
    # GM Key 47
    LOW_MID_TOM = auto(), BeatStudioNoteName.MED_TOM
    # GM Key 48
    HI_MID_TOM = auto(), BeatStudioNoteName.HI_TOM
