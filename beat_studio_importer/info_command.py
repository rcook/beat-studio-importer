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

from beat_studio_importer.import_ui import select_tracks
from beat_studio_importer.midi_source import MidiSource
from beat_studio_importer.note_name_map import DEFAULT_NOTE_NAME_MAP, NoteNameMap
from beat_studio_importer.region import Region
from beat_studio_importer.ui import print_key_value
from beat_studio_importer.user_error import UserError
from colorama import Fore, Style
from pathlib import Path


def do_info(path: Path, note_track_name: str | None, metadata_track_name: str | None, note_name_map: NoteNameMap | None) -> None:
    if not path.is_file():
        raise UserError(f"Input file {path} not found")

    source = MidiSource.load(path)
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

    print_key_value("Ticks per beat", source.ticks_per_beat)
    for region in regions:
        print(
            Fore.LIGHTYELLOW_EX,
            f"Region {region.region_id}",
            Style.RESET_ALL,
            sep="")
        beat = region.time_signature.basis.value[2]
        print_key_value("MIDI tempo", region.tempo)
        print_key_value("Time signature", region.time_signature)
        print_key_value(
            "QPM tempo (quarter notes per minute)",
            f"{region.qpm:.1f}")
        print_key_value(
            f"BPM tempo (beats per minute, beat={beat})",
            f"{region.bpm:.1f}")
