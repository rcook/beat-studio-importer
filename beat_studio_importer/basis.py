from beat_studio_importer.util import midi_tempo_to_qpm
from enum import Enum, auto, unique


@unique
class Basis(Enum):
    EIGHTH = auto(), 0.5, "eighth"
    QUARTER = auto(), 1.0, "quarter"
    DOTTED_QUARTER = auto(), 1.5, "dotted quarter"

    # Tempo as basis beats per minute
    def midi_tempo_to_bpm(self, tempo: int) -> float:
        qpm = midi_tempo_to_qpm(tempo)
        multiplier = self.value[1]
        return qpm / multiplier
