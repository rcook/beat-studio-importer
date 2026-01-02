from beat_studio_importer.basis import Basis
from enum import Enum, unique


@unique
class NoteValue(Enum):
    WHOLE = 1, Basis.WHOLE
    HALF = 2, Basis.HALF
    QUARTER = 4, Basis.QUARTER
    EIGHTH = 8, Basis.EIGHTH
    SIXTEENTH = 16, Basis.SIXTEENTH

    @staticmethod
    def from_denominator(value: int) -> "NoteValue":
        for member in NoteValue:
            if member.value[0] == value:
                return member
        raise ValueError(f"Invalid denominator {value}")
