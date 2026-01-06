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

from beat_studio_importer.arg_summary import ArgSummary
from beat_studio_importer.beat_studio_pattern import BeatStudioPattern
from beat_studio_importer.beat_studio_tempo import BEAT_STUDIO_TEMPO_MAX, BEAT_STUDIO_TEMPO_MIN, BeatStudioTempo
from beat_studio_importer.beat_studio_util import default_beat_studio_profile
from beat_studio_importer.constants import BEAT_STUDIO_STEP_COUNT_MAX, BEAT_STUDIO_STEP_COUNT_MIN, PROGRAM_NAME, PROGRAM_URL
from beat_studio_importer.midi_note_name_map import DEFAULT_MIDI_NOTE_NAME_MAP, MidiNoteNameMap
from beat_studio_importer.midi_util import summarize_midi_file
from beat_studio_importer.misc import MidiChannel, RegionId
from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.region import Region
from beat_studio_importer.tempos import midi_tempo_to_qpm
from beat_studio_importer.timeline import Timeline
from beat_studio_importer.ui import cprint, select_region
from beat_studio_importer.user_error import UserError
from colorama import Fore, Style
from datetime import datetime, timezone
from enum import Enum, auto, unique
from mido import MidiFile
from pathlib import Path
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from _typeshed import SupportsWrite


@unique
class PatternInfo(Enum):
    IDENTICAL_PATTERN_DEFINED = auto()
    PATTERN_NAME_IN_USE = auto()

    @staticmethod
    def find_existing(patterns_path: Path, pattern: BeatStudioPattern) -> "PatternInfo | None":
        patterns = BeatStudioPattern.load(patterns_path)
        for p in patterns:
            if pattern == p:
                return PatternInfo.IDENTICAL_PATTERN_DEFINED
            if pattern.name.lower() == p.name.lower():
                return PatternInfo.PATTERN_NAME_IN_USE
        return None


def do_import(
        path: Path,
        note_name_map: MidiNoteNameMap | None,
        channel: MidiChannel | None,
        region_id: RegionId | None,
        quantum: NoteValue, name: str | None,
        override_tempo: BeatStudioTempo | None,
        repeat: int | None,
        discard_boundary_hits: bool,
        add: bool,
        all: bool,
        args: ArgSummary) -> None:
    if not path.is_file():
        raise UserError(f"Input file {path} not found")

    file = MidiFile(path)
    summarize_midi_file(file)

    timeline = Timeline.build(file, channel=channel)
    regions = Region.build_all(
        timeline,
        discard_boundary_hits=discard_boundary_hits)

    note_name_map = note_name_map or DEFAULT_MIDI_NOTE_NAME_MAP

    if all:
        for region in regions:
            if name is None:
                region_name = f"{path.stem} region {region.id}"
            else:
                region_name = f"{name} region {region.id}"

            import_region(
                region=region,
                name=region_name,
                note_name_map=note_name_map,
                quantum=quantum,
                override_tempo=override_tempo,
                repeat=repeat,
                add=add,
                args=args.append("region", str(region.id)))
    else:
        region = select_region(path, regions, region_id)
        import_region(
            region=region,
            name=name or path.stem,
            note_name_map=note_name_map,
            quantum=quantum,
            override_tempo=override_tempo,
            repeat=repeat,
            add=add,
            args=args)


def import_region(region: Region, name: str, note_name_map: MidiNoteNameMap, quantum: NoteValue,  override_tempo: BeatStudioTempo | None, repeat: int | None, add: bool, args: ArgSummary) -> None:
    if override_tempo is None:
        qpm = midi_tempo_to_qpm(region.tempo)
        if not (BEAT_STUDIO_TEMPO_MIN <= qpm <= BEAT_STUDIO_TEMPO_MAX):
            raise UserError(
                f"Tempo {qpm} is outside allowed range ({BEAT_STUDIO_TEMPO_MIN}, {BEAT_STUDIO_TEMPO_MAX})")
        tempo = BeatStudioTempo.from_qpm(qpm)
    else:
        tempo = override_tempo

    pattern = region.render(
        name,
        note_name_map,
        quantum,
        tempo=tempo,
        repeat=repeat)

    if not (BEAT_STUDIO_STEP_COUNT_MIN <= pattern.step_count <= BEAT_STUDIO_STEP_COUNT_MAX):
        raise UserError(
            f"Number of steps {pattern.step_count} is outside allowed range ({BEAT_STUDIO_STEP_COUNT_MIN}, {BEAT_STUDIO_STEP_COUNT_MAX}): use a shorter pattern or specify repetitions using --repeat")

    if pattern.is_empty:
        cprint(
            Fore.LIGHTRED_EX,
            f"Skipping empty pattern in region {region.id}")
        return

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

        match PatternInfo.find_existing(patterns_path, pattern):
            case PatternInfo.IDENTICAL_PATTERN_DEFINED:
                print(
                    Fore.WHITE,
                    "An identical pattern ",
                    Fore.LIGHTBLUE_EX,
                    pattern.name,
                    Fore.WHITE,
                    " is already defined in ",
                    Fore.LIGHTCYAN_EX,
                    patterns_path,
                    Style.RESET_ALL,
                    sep="")
            case PatternInfo.PATTERN_NAME_IN_USE:
                print(
                    Fore.WHITE,
                    "Pattern name ",
                    Fore.LIGHTBLUE_EX,
                    pattern.name,
                    Fore.WHITE,
                    " is already in use in ",
                    Fore.LIGHTCYAN_EX,
                    patterns_path,
                    Style.RESET_ALL,
                    sep="")
            case None:
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


def write_pattern_output(pattern: BeatStudioPattern, region: Region, args: ArgSummary, file: "SupportsWrite[str]|None" = None) -> None:
    for line in summarize_pattern(pattern, region, args):
        print(line, file=file)
    pattern.print(file=file)


def summarize_pattern(pattern: BeatStudioPattern, region: Region, args: ArgSummary) -> list[str]:
    now = datetime.now(timezone.utc)
    comments = [
        f"# Pattern {pattern.name}",
        f"#   Time signature: {region.time_signature}",
        f"#   Pulse: {region.time_signature.pulse.display}",
        f"#   Tempo (BPM): {region.bpm}",
        f"#   Tempo (QPM): {region.qpm}",
        f"#   Tempo (MIDI): {region.tempo}",
        f"# Generated using {PROGRAM_NAME} ({PROGRAM_URL})",
        f"# Generated at {now.isoformat()}"
    ]
    if len(args.attrs) > 0:
        comments.append("# Parameters:")
        comments.extend(map(lambda p: f"#   {p[0]}={p[1]}", args.attrs))
    return comments
