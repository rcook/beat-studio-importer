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
from beat_studio_importer.beat_studio_util import default_patterns_beat_path
from beat_studio_importer.features import NEW_TIMELINE_FEATURE_ENABLED
from beat_studio_importer.import_ui import select_region, select_tracks
from beat_studio_importer.midi_source import MidiSource
from beat_studio_importer.midi_util import summarize_midi_file
from beat_studio_importer.note_name_map import DEFAULT_NOTE_NAME_MAP, NoteNameMap
from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.region import Region
from beat_studio_importer.region2 import Region2
from beat_studio_importer.timeline import Timeline
from beat_studio_importer.ui import cprint
from beat_studio_importer.user_error import UserError
from colorama import Fore, Style
from pathlib import Path


def do_import(path: Path, note_track_name: str | None, metadata_track_name: str | None, note_name_map: NoteNameMap | None, region_id: int | None, quantize: NoteValue, name: str | None, override_tempo: int | None, add: bool = False) -> None:
    if not path.is_file():
        raise UserError(f"Input file {path} not found")

    source = MidiSource.load(path)

    summarize_midi_file(source.file)
    print()

    if NEW_TIMELINE_FEATURE_ENABLED:
        timeline = Timeline.build(source.file)
        new_regions = Region2.build_all(timeline)
        for r in new_regions:
            cprint(
                Fore.LIGHTYELLOW_EX,
                f"Region ID {r.id}: {r.start_tick}-{r.end_tick}, tempo {r.tempo}, time_signature {r.time_signature}")
            for note in r.notes:
                cprint(Fore.LIGHTBLUE_EX, f"  {note}")
        print()

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

    region = select_region(source.path, regions, region_id)

    name = name or f"{source.path.stem} region {region.region_id}"
    pattern = region.render(name, quantize, override_tempo=override_tempo)

    print(Fore.LIGHTYELLOW_EX, end="")
    pattern.print()
    print(Style.RESET_ALL)

    if add:
        patterns_beat_path = default_patterns_beat_path()
        if is_existing_pattern(patterns_beat_path, pattern):
            print(
                Fore.WHITE,
                "Pattern ",
                Fore.LIGHTBLUE_EX,
                pattern.name,
                Fore.WHITE,
                " is already defined in ",
                Fore.LIGHTCYAN_EX,
                patterns_beat_path,
                Style.RESET_ALL,
                sep="")
        else:
            with patterns_beat_path.open("at") as f:
                pattern.print(file=f)
            print(
                Fore.WHITE,
                "Pattern ",
                Fore.LIGHTBLUE_EX,
                pattern.name,
                Fore.WHITE,
                " added to ",
                Fore.LIGHTCYAN_EX,
                patterns_beat_path,
                Style.RESET_ALL,
                sep="")


def is_existing_pattern(patterns_beat_path: Path, pattern: BeatStudioPattern) -> bool:
    patterns = BeatStudioPattern.load(patterns_beat_path)
    for p in patterns:
        if pattern == p:
            return True
    return False
