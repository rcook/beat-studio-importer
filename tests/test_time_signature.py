from beat_studio_importer.basis import Basis
from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.time_signature import TimeSignature
from tests.util import is_close_tempo
import pytest


class TestTimeSignature:
    def test_three_four(self) -> None:
        time_signature = TimeSignature(3, NoteValue.QUARTER)
        assert is_close_tempo(120, time_signature.midi_tempo_to_bpm(500_000))
        assert is_close_tempo(60, time_signature.midi_tempo_to_bpm(1_000_000))

    def test_four_four(self) -> None:
        time_signature = TimeSignature(4, NoteValue.QUARTER)
        assert is_close_tempo(120, time_signature.midi_tempo_to_bpm(500_000))
        assert is_close_tempo(60, time_signature.midi_tempo_to_bpm(1_000_000))

    def test_seven_eight(self) -> None:
        time_signature = TimeSignature(7, NoteValue.EIGHTH)
        assert is_close_tempo(240, time_signature.midi_tempo_to_bpm(500_000))
        assert is_close_tempo(120, time_signature.midi_tempo_to_bpm(1_000_000))

    def test_twelve_eight(self) -> None:
        time_signature = TimeSignature(7, NoteValue.EIGHTH)
        assert is_close_tempo(240, time_signature.midi_tempo_to_bpm(500_000))
        assert is_close_tempo(120, time_signature.midi_tempo_to_bpm(1_000_000))

    # Reference: https://en.wikipedia.org/wiki/Time_signature
    @pytest.mark.parametrize("numerator, denominator, expected", [
        # Simple metre
        (1, NoteValue.WHOLE, Basis.WHOLE),
        (1, NoteValue.SIXTEENTH, Basis.SIXTEENTH),
        (2, NoteValue.HALF, Basis.HALF),
        (2, NoteValue.EIGHTH, Basis.EIGHTH),
        (3, NoteValue.WHOLE, Basis.WHOLE),
        (3, NoteValue.QUARTER, Basis.QUARTER),
        # Compound metre
        (6, NoteValue.EIGHTH, Basis.DOTTED_QUARTER),
        (9, NoteValue.EIGHTH, Basis.DOTTED_QUARTER),
        (12, NoteValue.EIGHTH, Basis.DOTTED_QUARTER),
        (15, NoteValue.EIGHTH, Basis.DOTTED_QUARTER),
        (6, NoteValue.SIXTEENTH, Basis.DOTTED_EIGHTH),
        (9, NoteValue.SIXTEENTH, Basis.DOTTED_EIGHTH),
        (12, NoteValue.SIXTEENTH, Basis.DOTTED_EIGHTH),
        (15, NoteValue.SIXTEENTH, Basis.DOTTED_EIGHTH),
        # Complex metre
        (5, NoteValue.QUARTER, Basis.QUARTER),
        (8, NoteValue.EIGHTH, Basis.EIGHTH),
        (7, NoteValue.SIXTEENTH, Basis.SIXTEENTH)
    ])
    def test_basis(self, numerator: int, denominator: NoteValue, expected: Basis) -> None:
        time_signature = TimeSignature(
            numerator=numerator,
            denominator=denominator)
        assert time_signature.basis is expected
