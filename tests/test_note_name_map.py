from beat_studio_importer.beat_studio_note_name import BeatStudioNoteName
from beat_studio_importer.note_name import NoteName
from beat_studio_importer.note_name_map import DEFAULT_NOTE_NAME_MAP


class TestNoteNameMap:
    def test_basics(self) -> None:
        note_name = DEFAULT_NOTE_NAME_MAP[48]
        assert note_name is NoteName.HI_MID_TOM
        assert note_name.value == (6, BeatStudioNoteName.HI_TOM)
