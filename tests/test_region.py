from beat_studio_importer.midi_source import MidiSource
from beat_studio_importer.note_name_map import DEFAULT_NOTE_NAME_MAP
from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.region import Region
from io import StringIO
from pathlib import Path


SAMPLES_DIR: Path = Path(__file__).parent.parent / "samples"


def render_to_lines(region: Region) -> list[str]:
    with StringIO() as f:
        region.render("name", NoteValue.SIXTEENTH).print(file=f)
        return f.getvalue().split("\n")


class TestRegion:
    def test_export_1_region_1(self):
        source = MidiSource.load(SAMPLES_DIR / "reaper/smf-type-1.mid")
        assert len(source.tracks) == 2

        note_track = source.tracks[1]
        metadata_track = source.tracks[0]

        regions = Region.from_midi_messages(
            note_track,
            metadata_track,
            DEFAULT_NOTE_NAME_MAP,
            source.ticks_per_beat)
        assert len(regions) == 2

        assert render_to_lines(regions[0]) == [
            "[\"name\" - 20 - 100 - 16 - 5/4]",
            "CRASH     : ....................",
            "CRASH2    : ....................",
            "HI-HAT    : ....................",
            "HI-TOM    : ....................",
            "KICK      : 6.......6.6.....6...",
            "LOW-TOM   : ....................",
            "MED-TOM   : ....................",
            "OPEN-HIHAT: ....................",
            "RIDE      : ....................",
            "SNARE     : ....6.......6.....6.",
            ""
        ]

        # TBD (Bug): Tempo should be 60!
        assert render_to_lines(regions[1]) == [
            "[\"name\" - 28 - 120 - 16 - 7/8]",
            "CRASH     : ............................",
            "CRASH2    : ............................",
            "HI-HAT    : ..............7.7.7.7.7.7.7.",
            "HI-TOM    : ............................",
            "KICK      : 6.6....6..6.6.7...7...7...7.",
            "LOW-TOM   : ............................",
            "MED-TOM   : ............................",
            "OPEN-HIHAT: ............................",
            "RIDE      : ............................",
            "SNARE     : ....6...6....6..7...7...7...",
            ""
        ]
