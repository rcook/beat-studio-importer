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

from beat_studio_importer.beat_studio_pattern import BeatStudioPattern
from beat_studio_importer.beat_studio_util import default_beat_studio_profile
from beat_studio_importer.import_ui import select_tracks
from beat_studio_importer.midi_source import MidiSource
from beat_studio_importer.midi_util import summarize_midi_file
from beat_studio_importer.note_name_map import DEFAULT_NOTE_NAME_MAP, NoteNameMap
from beat_studio_importer.region import Region
from beat_studio_importer.table import Table
from beat_studio_importer.ui import cprint, print_key_value
from beat_studio_importer.user_error import UserError
from colorama import Fore
from pathlib import Path


def do_info(path: Path | None, note_track_name: str | None, metadata_track_name: str | None, note_name_map: NoteNameMap | None) -> None:
    show_beat_studio_info()

    if path is not None:
        show_file_info(
            path=path,
            note_track_name=note_track_name,
            metadata_track_name=metadata_track_name,
            note_name_map=note_name_map)


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


def show_file_info(path: Path, note_track_name: str | None, metadata_track_name: str | None, note_name_map: NoteNameMap | None) -> None:
    if not path.is_file():
        raise UserError(f"Input file {path} not found")

    source = MidiSource.load(path)

    summarize_midi_file(source.file)

    note_track, metadata_track = select_tracks(
        source.path,
        source.tracks,
        note_track_name,
        metadata_track_name)

    note_name_map = note_name_map or DEFAULT_NOTE_NAME_MAP

    regions = Region.from_midi_messages(
        note_track,
        metadata_track,
        note_name_map,
        source.ticks_per_beat)

    for region in regions:
        print()
        cprint(Fore.LIGHTYELLOW_EX, f"Region {region.region_id}")
        beat = region.time_signature.basis.value[2]
        with Table((None, None, "{}", Fore.LIGHTBLUE_EX), (None, None, "{}", Fore.LIGHTCYAN_EX), column_sep="  ") as table:
            table.add_row("MIDI tempo", region.tempo)
            table.add_row("Time signature", region.time_signature)
            table.add_row(
                "QPM tempo (quarter notes per minute)",
                f"{region.qpm:.1f}")
            table.add_row(
                f"BPM tempo (beats per minute, beat={beat})",
                f"{region.bpm:.1f}")
            table.print()
