# Copyright (c) 2026 Richard Cook
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

from beat_studio_importer.midi_source import MidiSource
from beat_studio_importer.note_name_map import DEFAULT_NOTE_NAME_MAP
from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.region import Region
from io import StringIO
from pathlib import Path
from tests.util import is_close_tempo


SAMPLES_DIR: Path = Path(__file__).parent.parent / "samples"


def render_to_lines(region: Region, print_test_case: bool = False) -> list[str]:
    with StringIO() as f:
        region.render("name", NoteValue.SIXTEENTH).print(file=f)
        lines = f.getvalue().split("\n")
    if print_test_case:
        line_count = len(lines)
        print("[")
        for i, line in enumerate(lines, 1):
            s = line.replace("\"", "\\\"")
            if i == line_count:
                print(f"  \"{s}\"")
            else:
                print(f"  \"{s}\",")
        print("]")
    return lines


class TestRegion:
    def test_basics(self) -> None:
        source = MidiSource.load(SAMPLES_DIR / "reaper" / "smf-type-1.mid")
        assert len(source.tracks) == 2

        note_track = source.tracks[1]
        metadata_track = source.tracks[0]

        regions = Region.from_midi_messages(
            note_track,
            metadata_track,
            DEFAULT_NOTE_NAME_MAP,
            source.ticks_per_beat)
        assert len(regions) == 5

        assert is_close_tempo(100, regions[0].qpm)
        assert is_close_tempo(100, regions[0].bpm)
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

        assert is_close_tempo(120, regions[1].qpm)
        assert is_close_tempo(240, regions[1].bpm)
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

        assert is_close_tempo(120, regions[2].qpm)
        assert is_close_tempo(120, regions[2].bpm)
        assert render_to_lines(regions[2]) == [
            "[\"name\" - 16 - 120 - 16 - 4/4]",
            "CRASH     : ................",
            "CRASH2    : ................",
            "HI-HAT    : ................",
            "HI-TOM    : ................",
            "KICK      : 7...7...7...7...",
            "LOW-TOM   : ................",
            "MED-TOM   : ................",
            "OPEN-HIHAT: ................",
            "RIDE      : ................",
            "SNARE     : ................",
            ""
        ]

        assert is_close_tempo(60, regions[3].qpm)
        assert is_close_tempo(60, regions[3].bpm)
        assert render_to_lines(regions[3]) == [
            "[\"name\" - 16 - 60 - 16 - 4/4]",
            "CRASH     : ................",
            "CRASH2    : ................",
            "HI-HAT    : ................",
            "HI-TOM    : ................",
            "KICK      : 7...7...7...7...",
            "LOW-TOM   : ................",
            "MED-TOM   : ................",
            "OPEN-HIHAT: ................",
            "RIDE      : ................",
            "SNARE     : ................",
            ""
        ]

        assert is_close_tempo(180, regions[4].qpm)
        assert is_close_tempo(120, regions[4].bpm)
        assert render_to_lines(regions[4]) == [
            "[\"name\" - 24 - 180 - 16 - 12/8]",
            "CRASH     : ........................",
            "CRASH2    : ........................",
            "HI-HAT    : ........................",
            "HI-TOM    : ........................",
            "KICK      : ..7.7...7.7...7.7...7.7.",
            "LOW-TOM   : ........................",
            "MED-TOM   : ........................",
            "OPEN-HIHAT: ........................",
            "RIDE      : ........................",
            "SNARE     : 7.....7.....7.....7.....",
            ""
        ]

    def test_boundary(self) -> None:
        source = MidiSource.load(SAMPLES_DIR / "seven-eight.mid")
        assert len(source.tracks) == 2

        note_track = source.tracks[1]
        metadata_track = source.tracks[0]

        regions = Region.from_midi_messages(
            note_track,
            metadata_track,
            DEFAULT_NOTE_NAME_MAP,
            source.ticks_per_beat,
            silently_discard_hit_on_boundary=True)
        assert len(regions) == 1

        assert is_close_tempo(120, regions[0].qpm)
        assert is_close_tempo(240, regions[0].bpm)
        assert render_to_lines(regions[0]) == [
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
            "",
        ]

        regions = Region.from_midi_messages(
            note_track,
            metadata_track,
            DEFAULT_NOTE_NAME_MAP,
            source.ticks_per_beat,
            silently_discard_hit_on_boundary=False)
        assert len(regions) == 1

        assert is_close_tempo(120, regions[0].qpm)
        assert is_close_tempo(240, regions[0].bpm)
        assert render_to_lines(regions[0]) == [
            "[\"name\" - 42 - 120 - 16 - 7/8]",
            "CRASH     : ..........................................",
            "CRASH2    : ..........................................",
            "HI-HAT    : ..............7.7.7.7.7.7.7...............",
            "HI-TOM    : ..........................................",
            "KICK      : 6.6....6..6.6.7...7...7...7.7.............",
            "LOW-TOM   : ..........................................",
            "MED-TOM   : ..........................................",
            "OPEN-HIHAT: ..........................................",
            "RIDE      : ..........................................",
            "SNARE     : ....6...6....6..7...7...7.................",
            ""
        ]
