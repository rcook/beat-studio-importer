from enum import Enum, unique


@unique
class NoteValue(Enum):
    WHOLE = 1
    HALF = 2
    QUARTER = 4
    EIGHT = 8
    SIXTEENTH = 16

    @staticmethod
    def from_denominator(value: int) -> "NoteValue":
        for member in NoteValue:
            if member.value == value:
                return member
        raise ValueError(f"Invalid denominator {value}")
