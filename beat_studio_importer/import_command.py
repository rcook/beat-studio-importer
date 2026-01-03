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

from typing import TYPE_CHECKING
from beat_studio_importer.beat_studio_pattern import BeatStudioPattern
from beat_studio_importer.beat_studio_util import default_beat_studio_profile
from beat_studio_importer.constants import PROGRAM_NAME, PROGRAM_URL
from beat_studio_importer.import_ui import select_region
from beat_studio_importer.midi_source import MidiSource
from beat_studio_importer.midi_util import summarize_midi_file
from beat_studio_importer.misc import BeatStudioTempo, MidiChannel, RegionId
from beat_studio_importer.note_name_map import DEFAULT_NOTE_NAME_MAP, NoteNameMap
from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.region import Region
from beat_studio_importer.timeline import Timeline
from beat_studio_importer.user_error import UserError
from colorama import Fore, Style
from datetime import datetime, timezone
from pathlib import Path


if TYPE_CHECKING:
    from _typeshed import SupportsWrite


def do_import(path: Path, note_name_map: NoteNameMap | None, channel: MidiChannel | None, region_id: RegionId | None, quantize: NoteValue, name: str | None, override_tempo: BeatStudioTempo | None, repeat: int | None, add: bool, args: list[tuple[str, str]]) -> None:
    if not path.is_file():
        raise UserError(f"Input file {path} not found")

    source = MidiSource.load(path)

    summarize_midi_file(source.file)
    print()

    timeline = Timeline.build(source.file, channel=channel)
    regions = Region.build_all(timeline)
    region = select_region(source.path, regions, region_id)

    name = name or f"{source.path.stem} region {region.id}"
    note_name_map = note_name_map or DEFAULT_NOTE_NAME_MAP
    pattern = region.render(
        name,
        note_name_map,
        quantize,
        override_tempo=override_tempo,
        repeat=repeat)

    print(Fore.LIGHTYELLOW_EX, end="")
    write_pattern_output(pattern, region, args)
    print(Style.RESET_ALL)

    if add:
        profile = default_beat_studio_profile()
        if profile is None:
            raise UserError("Cannot find Beat Studio profile")

        patterns_path = profile[1]
        if patterns_path is None:
            raise UserError("Cannot find Beat Studio patterns file")

        if is_existing_pattern(patterns_path, pattern):
            print(
                Fore.WHITE,
                "Pattern ",
                Fore.LIGHTBLUE_EX,
                pattern.name,
                Fore.WHITE,
                " is already defined in ",
                Fore.LIGHTCYAN_EX,
                patterns_path,
                Style.RESET_ALL,
                sep="")
        else:
            with patterns_path.open("at") as f:
                print(file=f)
                write_pattern_output(pattern, region, args, file=f)
            print(
                Fore.WHITE,
                "Pattern ",
                Fore.LIGHTBLUE_EX,
                pattern.name,
                Fore.WHITE,
                " added to ",
                Fore.LIGHTCYAN_EX,
                patterns_path,
                Style.RESET_ALL,
                sep="")


def write_pattern_output(pattern: BeatStudioPattern, region: Region, args: list[tuple[str, str]], file: "SupportsWrite[str]|None" = None) -> None:
    for line in summarize_pattern(pattern, region, args):
        print(line, file=file)
    pattern.print(file=file)


def summarize_pattern(pattern: BeatStudioPattern, region: Region, args: list[tuple[str, str]]) -> list[str]:
    now = datetime.now(timezone.utc)
    comments = [
        f"# Pattern {pattern.name}",
        f"#   Time signature: {region.time_signature}",
        f"#   Pulse: {region.time_signature.pulse.value[2]}",
        f"#   Tempo (BPM): {region.bpm}",
        f"#   Tempo (QPM): {region.qpm}",
        f"#   Tempo (MIDI): {region.tempo}",
        f"# Generated using {PROGRAM_NAME} ({PROGRAM_URL})",
        f"# Generated at {now.isoformat()}"
    ]
    if len(args) > 0:
        comments.append("# Parameters:")
        comments.extend(map(lambda p: f"#   {p[0]}={p[1]}", args))
    return comments


def is_existing_pattern(patterns_path: Path, pattern: BeatStudioPattern) -> bool:
    patterns = BeatStudioPattern.load(patterns_path)
    for p in patterns:
        if pattern == p:
            return True
    return False
