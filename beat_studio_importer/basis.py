from beat_studio_importer.util import midi_tempo_to_qpm
from enum import Enum, auto, unique


@unique
class Basis(Enum):
    SIXTEENTH = auto(), 0.25, "sixteenth"
    EIGHTH = auto(), 0.5, "eighth"
    DOTTED_EIGHTH = auto(), 0.7, "dotted eight"
    QUARTER = auto(), 1.0, "quarter"
    DOTTED_QUARTER = auto(), 1.5, "dotted quarter"
    HALF = auto(), 2.0, "half"
    WHOLE = auto(), 4.0, "whole"

    # Tempo as basis beats per minute
    def midi_tempo_to_bpm(self, tempo: int) -> float:
        qpm = midi_tempo_to_qpm(tempo)
        multiplier = self.value[1]
        return qpm / multiplier
