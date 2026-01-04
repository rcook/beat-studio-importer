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

from mido import MidiFile
from beat_studio_importer.beat_studio_pattern import BeatStudioPattern
from beat_studio_importer.beat_studio_util import default_beat_studio_profile
from beat_studio_importer.midi_util import summarize_midi_file
from beat_studio_importer.region import Region
from beat_studio_importer.table import Table
from beat_studio_importer.timeline import Timeline
from beat_studio_importer.ui import cprint, print_key_value
from beat_studio_importer.user_error import UserError
from colorama import Fore
from pathlib import Path


def do_info(path: Path | None) -> None:
    show_beat_studio_info()

    if path is not None:
        show_file_info(path=path)


def show_beat_studio_info() -> None:
    profile = default_beat_studio_profile()
    if profile is None:
        cprint(Fore.LIGHTRED_EX, "Cannot find Beat Studio profile")
    else:
        print_key_value("Beat Studio profile directory", profile[0])

        patterns_path = profile[1]
        if patterns_path is not None:
            print_key_value("Beat Studio patterns file", patterns_path)

            patterns = BeatStudioPattern.load(patterns_path)
            if len(patterns) > 0:
                cprint(Fore.LIGHTBLUE_EX, "Available patterns:")
                for pattern in sorted(patterns, key=lambda p: p.name):
                    cprint("  ", Fore.LIGHTCYAN_EX, pattern.name)

    print()


def show_file_info(path: Path) -> None:
    if not path.is_file():
        raise UserError(f"Input file {path} not found")

    file = MidiFile(path)
    summarize_midi_file(file)

    timeline = Timeline.build(file)
    regions = Region.build_all(timeline)
    for region in regions:
        print()
        cprint(Fore.LIGHTYELLOW_EX, f"Region {region.id}")
        with Table((None, None, "{}", Fore.LIGHTBLUE_EX), (None, None, "{}", Fore.LIGHTCYAN_EX), column_sep="  ") as table:
            table.add_row("MIDI tempo", region.tempo)
            table.add_row("Time signature", region.time_signature)
            table.add_row(
                "QPM tempo (quarter notes per minute)",
                f"{region.qpm:.1f}")
            table.add_row(
                f"BPM tempo (beats per minute, beat={region.time_signature.pulse.display})",
                f"{region.bpm:.1f}")
            table.print()
