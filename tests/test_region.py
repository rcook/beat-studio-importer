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

from beat_studio_importer.midi_note_name_map import DEFAULT_MIDI_NOTE_NAME_MAP
from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.region import Region
from beat_studio_importer.timeline import Timeline
from io import StringIO
from mido import MidiFile
from pathlib import Path
from tests.util import is_close_tempo
import pytest


SAMPLES_DIR: Path = Path(__file__).parent.parent / "samples"


def render_to_str(region: Region, quantum: NoteValue | None = None) -> str:
    with StringIO() as f:
        pattern = region.render(
            "name",
            DEFAULT_MIDI_NOTE_NAME_MAP,
            quantum or NoteValue.SIXTEENTH)
        pattern.print(file=f)
        return f.getvalue()


def render_to_lines(region: Region, quantum: NoteValue | None = None, print_test_case: bool = False) -> list[str]:
    s = render_to_str(region=region, quantum=quantum)
    lines = s.split("\n")
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
        file = MidiFile(SAMPLES_DIR / "example-0.mid")
        assert len(file.tracks) == 2

        timeline = Timeline.build(file)

        regions = Region.build_all(timeline)
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
        file = MidiFile(SAMPLES_DIR / "seven-eight.mid")
        assert len(file.tracks) == 2

        timeline = Timeline.build(file)

        regions = Region.build_all(timeline, discard_boundary_hits=True)
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

        regions = Region.build_all(timeline, discard_boundary_hits=False)
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

    @pytest.mark.parametrize("path, expected", [
        ("Demo_Basic_Rock.mid", """[\"name\" - 32 - 120 - 16 - 4/4]
CRASH     : ................................
CRASH2    : ................................
HI-HAT    : 6.3.9.3.6.3.6.3.6.3.6.3.6.3.6.3.
HI-TOM    : ................................
KICK      : 9.......7.......7.......7.......
LOW-TOM   : ................................
MED-TOM   : ................................
OPEN-HIHAT: ................................
RIDE      : ................................
SNARE     : ....9.......7.......7.......8..."""),
        ("Demo_Easy_beat.mid", """[\"name\" - 64 - 120 - 16 - 4/4]
CRASH     : 5...............................................................
CRASH2    : ................................................................
HI-HAT    : 6.2.6.2.6.2.6.2.6.2.6.516.2.6.2.6.2.6.2.6.2.6.2.6.2.6.2.6.2.6...
HI-TOM    : ................................................................
KICK      : 7.......7.7.....7.......7.7.....7.......7.7.....7.......7.7.....
LOW-TOM   : ................................................................
MED-TOM   : ................................................................
OPEN-HIHAT: ..............................................................2.
RIDE      : ................................................................
SNARE     : ....5.......6.......6.......6.......6.......6.......6.......6..."""),
        ("Demo_Fill.mid", """[\"name\" - 32 - 110 - 16 - 4/4]
CRASH     : ................................
CRASH2    : ......................7.........
HI-HAT    : 7.3.7.3.7.3.7.3.................
HI-TOM    : ................4.........3.....
KICK      : 8.......8.......8....7........6.
LOW-TOM   : ....................7........2..
MED-TOM   : ...................6........3...
OPEN-HIHAT: ................................
RIDE      : ................................
SNARE     : ....7.......8....76...7........."""),
        ("Demo_Groove.mid", """[\"name\" - 32 - 95 - 16 - 4/4]
CRASH     : ................................
CRASH2    : ................................
HI-HAT    : 7.4.7.4.7.4.7.4.7.4.7.3.7.4.7.3.
HI-TOM    : ................................
KICK      : 9..8.......8....9..8.......8....
LOW-TOM   : ................................
MED-TOM   : ................................
OPEN-HIHAT: ................................
RIDE      : ................................
SNARE     : .1..71.1.2..81.2.1..71.1.2..81.2"""),
        ("Demo_Just_Hihat.mid", """[\"name\" - 32 - 120 - 16 - 4/4]
CRASH     : ................................
CRASH2    : ................................
HI-HAT    : 7.3.6.3.6.3.715.7.3.6.3.7.3.613.
HI-TOM    : ................................
KICK      : ................................
LOW-TOM   : ................................
MED-TOM   : ................................
OPEN-HIHAT: ................................
RIDE      : ................................
SNARE     : ................................""")
    ])
    def test_demos(self, path: Path, expected: str) -> None:
        file = MidiFile(SAMPLES_DIR / "0.3.3-alpha" / path)
        assert len(file.tracks) == 1
        timeline = Timeline.build(file)
        regions = Region.build_all(timeline, discard_boundary_hits=True)
        assert len(regions) == 1
        s = render_to_str(regions[0])
        assert s.strip() == expected.strip()

    def test_tempo_time_signature_bug(self) -> None:
        def summarize(region: Region) -> tuple[int, int, int, str, int]:
            return region.start_tick, region.end_tick, region.tempo, str(region.time_signature), len(region.notes)

        file = MidiFile(SAMPLES_DIR / "example-2.mid")
        assert len(file.tracks) == 8
        timeline = Timeline.build(file)
        assert timeline.ppqn == 960
        assert len(timeline.events) == 4032
        regions = Region.build_all(timeline, discard_boundary_hits=True)
        assert len(regions) == 13
        assert summarize(regions[0]) == (0, 326400, 500000, "4/4", 2751)
        assert summarize(regions[1]) == (326400, 339360, 500000, "9/8", 101)
        assert summarize(regions[2]) == (339360, 342720, 500000, "7/8", 19)
        assert summarize(regions[3]) == (342720, 355680, 500000, "9/8", 109)
        assert summarize(regions[4]) == (355680, 360480, 500000, "5/4", 40)
        assert summarize(regions[5]) == (360480, 373920, 500000, "7/8", 166)
        assert summarize(regions[6]) == (373920, 389280, 500000, "4/4", 207)
        assert summarize(regions[7]) == (389280, 404640, 500000, "4/4", 143)
        assert summarize(regions[8]) == (404640, 458400, 500000, "7/4", 545)
        assert summarize(regions[9]) == (458400, 519840, 500000, "4/4", 562)
        assert summarize(regions[10]) == (519840, 619680, 500000, "4/4", 666)
        assert summarize(regions[11]) == (619680, 646560, 500000, "7/4", 236)
        assert summarize(regions[12]) == (646560, 669600, 500000, "4/4", 110)

    def test_quantization(self) -> None:
        file = MidiFile(SAMPLES_DIR / "example-3.mid")
        assert len(file.tracks) == 2
        timeline = Timeline.build(file)
        assert timeline.ppqn == 960
        assert len(timeline.events) == 13
        regions = Region.build_all(timeline, discard_boundary_hits=True)
        assert len(regions) == 1

        # Quantize to 64ths
        expected = """[\"name\" - 64 - 120 - 64 - 4/4]
CRASH     : ................................................................
CRASH2    : ................................................................
HI-HAT    : 5.......6.......6.......5.......6.......5.......6.......6.......
HI-TOM    : ................................................................
KICK      : 9...............................9...............................
LOW-TOM   : ................................................................
MED-TOM   : ................................................................
OPEN-HIHAT: ................................................................
RIDE      : ................................................................
SNARE     : ................9...............................9..............."""
        s = render_to_str(regions[0], quantum=NoteValue.SIXTY_FOURTH)
        assert s.strip() == expected.strip()

        # Quantize to 16ths
        expected = """[\"name\" - 16 - 120 - 16 - 4/4]
CRASH     : ................
CRASH2    : ................
HI-HAT    : 5.6.6.5.6.5.6.6.
HI-TOM    : ................
KICK      : 9.......9.......
LOW-TOM   : ................
MED-TOM   : ................
OPEN-HIHAT: ................
RIDE      : ................
SNARE     : ....9.......9..."""
        s = render_to_str(regions[0], quantum=NoteValue.SIXTEENTH)
        print(s)
        assert s.strip() == expected.strip()
