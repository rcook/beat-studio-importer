from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.time_signature import TimeSignature
from tests.util import is_close_tempo


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
