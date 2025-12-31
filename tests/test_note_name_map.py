from beat_studio_importer.note_name import NoteName
from beat_studio_importer.note_name_map import DEFAULT_NOTE_NAME_MAP


class TestNoteNameMap:
    def test_basics(self):
        assert DEFAULT_NOTE_NAME_MAP[47] is NoteName.MID_TOM_HIT
