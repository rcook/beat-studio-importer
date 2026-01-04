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

from argparse import _SubParsersAction, ArgumentParser, ArgumentTypeError, BooleanOptionalAction, Namespace
from beat_studio_importer.beat_studio_tempo import BEAT_STUDIO_TEMPO_MAX, BEAT_STUDIO_TEMPO_MIN, BeatStudioTempo
from beat_studio_importer.constants import PROGRAM_NAME, PROGRAM_URL
from beat_studio_importer.import_command import do_import
from beat_studio_importer.info_command import do_info
from beat_studio_importer.midi_note_name_map import MidiNoteNameMap
from beat_studio_importer.misc import MidiChannel, RegionId
from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.play_command import do_play
from beat_studio_importer.remap_command import do_remap
from beat_studio_importer.user_error import UserError
from colorama import Fore, Style
from pathlib import Path
from typing import Callable, Protocol, cast, runtime_checkable
import sys


type ArgsType = type
type Func[T] = Callable[[T], None]


def summarize_args(args: object) -> list[tuple[str, str]]:
    def render_value(value: object) -> str:
        match value:
            case bool() as x: return str(x).lower()
            case _: return str(value)

    attrs: list[tuple[str, str]] = []

    for name in dir(args):
        if name.startswith("_") or name in ["add", "handler"]:
            continue
        value = cast(object, getattr(args, name))
        if value is None:
            continue

        attrs.append((name, render_value(value)))

    return sorted(attrs, key=lambda p: p[0])


@runtime_checkable
class ImportArgs(Protocol):
    @property
    def path(self) -> Path: ...

    @property
    def note_name_path(self) -> Path | None: ...

    @property
    def channel(self) -> int | None: ...

    @property
    def region(self) -> int | None: ...

    @property
    def quantize(self) -> int: ...

    @property
    def override_tempo(self) -> int | None: ...

    @property
    def name(self) -> str | None: ...

    @property
    def repeat(self) -> int | None: ...

    @property
    def add(self) -> bool: ...

    @property
    def discard_boundary_hits(self) -> bool: ...


def do_import_args(args: ImportArgs) -> None:
    def wrap_optional[T, U](func: Callable[[T], U], obj: T | None) -> U | None:
        return None if obj is None else func(obj)

    do_import(
        path=args.path,
        note_name_map=wrap_optional(MidiNoteNameMap.load, args.note_name_path),
        channel=wrap_optional(MidiChannel, args.channel),
        region_id=wrap_optional(RegionId, args.region),
        quantize=NoteValue.from_int(args.quantize),
        name=args.name,
        override_tempo=wrap_optional(BeatStudioTempo, args.override_tempo),
        repeat=args.repeat,
        add=args.add,
        discard_boundary_hits=args.discard_boundary_hits,
        args=summarize_args(args))


@runtime_checkable
class InfoArgs(Protocol):
    @property
    def path(self) -> Path | None: ...

    @property
    def dump(self) -> bool: ...

    @property
    def exclude(self) -> list[str] | None: ...


def do_info_args(args: InfoArgs) -> None:
    do_info(path=args.path, dump=args.dump, exclude=args.exclude)


@runtime_checkable
class PlayArgs(Protocol):
    @property
    def path(self) -> Path: ...

    @property
    def port_name(self) -> str | None: ...

    @property
    def force_channel_10(self) -> bool | None: ...


def do_play_args(args: PlayArgs) -> None:
    do_play(
        path=args.path,
        port_name=args.port_name,
        force_channel_10=args.force_channel_10 or False)


@runtime_checkable
class RemapArgs(Protocol):
    @property
    def path(self) -> Path: ...

    @property
    def output_path(self) -> Path: ...


def do_remap_args(args: RemapArgs) -> None:
    do_remap(path=args.path, output_path=args.output_path)


def resolve_path(cwd: Path, s: str) -> Path:
    return (cwd / Path(s).expanduser()).resolve()


def add_path_arg(parser: ArgumentParser, cwd: Path, optional: bool = False) -> None:
    def resolved_path(s: str) -> Path:
        return resolve_path(cwd, s)

    _ = parser.add_argument(
        dest="path",
        metavar="PATH",
        type=resolved_path,
        nargs="?" if optional else None,
        help="path of file to import")


def add_output_path_arg(parser: ArgumentParser, cwd: Path, optional: bool = False) -> None:
    def resolved_path(s: str) -> Path:
        return resolve_path(cwd, s)

    _ = parser.add_argument(
        dest="output_path",
        metavar="OUTPUT_PATH",
        type=resolved_path,
        nargs="?" if optional else None,
        help="output path")


def add_note_map_path_arg(parser: ArgumentParser, cwd: Path) -> None:
    def resolved_path(s: str) -> Path:
        return resolve_path(cwd, s)

    _ = parser.add_argument(
        "--note-name-path",
        "-n",
        dest="note_name_path",
        metavar="NOTE_NAME_PATH",
        type=resolved_path,
        default=None,
        required=False,
        help="path to note name file")


def main(cwd: Path, argv: list[str]) -> None:
    def add_parser[T](parsers: "_SubParsersAction[ArgumentParser]", name: str, help: str, args_cls: type[T], func: Func[T]) -> ArgumentParser:
        p = parsers.add_parser(
            name=name,
            help=help,
            description=help[0].upper() + help[1:])
        p.set_defaults(handler=(args_cls, func))
        return p

    def beat_studio_tempo(s: str) -> BeatStudioTempo:
        try:
            return BeatStudioTempo(int(s))
        except ValueError:
            raise ArgumentTypeError(
                f"tempo {s} is outside allowed range ({BEAT_STUDIO_TEMPO_MIN}, {BEAT_STUDIO_TEMPO_MAX})")

    parser = ArgumentParser(
        prog=PROGRAM_NAME,
        description="Import patterns from MIDI files into Beat Studio patterns.beat file",
        epilog=PROGRAM_URL)
    parsers = parser.add_subparsers(required=True)

    p = add_parser(
        parsers,
        "import",
        "import pattern from MIDI file",
        ImportArgs,  # type: ignore[type-abstract]
        do_import_args)
    add_path_arg(p, cwd)
    add_note_map_path_arg(p, cwd)
    _ = p.add_argument(
        "--channel",
        "-c",
        dest="channel",
        metavar="CHANNEL",
        type=int,
        choices=range(1, 17),
        default=10,
        help="MIDI channel")
    _ = p.add_argument(
        "--region",
        "-r",
        dest="region",
        metavar="REGION",
        type=int,
        default=None,
        help="region index")
    _ = p.add_argument(
        "--quantize",
        "-q",
        dest="quantize",
        metavar="QUANTIZE",
        type=int,
        choices=sorted(member.int_value for member in NoteValue),
        default=NoteValue.SIXTEENTH.int_value,
        help="quantize step (4=quarter note, 8=eighth etc.)")
    _ = p.add_argument(
        "--name",
        dest="name",
        metavar="NAME",
        type=str,
        default=None,
        help="pattern name")
    _ = p.add_argument(
        "--tempo",
        dest="override_tempo",
        metavar="OVERRIDE_TEMPO",
        type=beat_studio_tempo,
        default=None,
        help="override tempo in output (to work around Beat Studio tempo bug)")
    _ = p.add_argument(
        "--repeat",
        dest="repeat",
        metavar="REPEAT",
        type=int,
        help="number of times to repeat hits")
    _ = p.add_argument(
        "--add",
        "-a",
        dest="add",
        metavar="ADD",
        action=BooleanOptionalAction,
        default=False,
        help="add new pattern to Beat Studio patterns.beat file")
    _ = p.add_argument(
        "--discard-boundary-hits",
        "-d",
        dest="discard_boundary_hits",
        metavar="DISCARD_BOUNDARY_HITS",
        action=BooleanOptionalAction,
        default=True,
        help="discard notes at the end of the last measure (default) or extend pattern by a whole measure to include event")

    p = add_parser(
        parsers,
        "info",
        "show information about Beat Studio profile and (optionally) contents of a MIDI file",
        InfoArgs,  # type: ignore[type-abstract]
        do_info_args)
    add_path_arg(p, cwd, optional=True)
    _ = p.add_argument(
        "--dump",
        dest="dump",
        metavar="DUMP",
        action=BooleanOptionalAction,
        default=False,
        help="dump out list of MIDI events")
    _ = p.add_argument(
        "--exclude",
        dest="exclude",
        metavar="EXCLUDE",
        type=str,
        nargs="+",
        default=None,
        help="filter out given message types")

    p = add_parser(
        parsers,
        "play",
        "play MIDI file",
        PlayArgs,  # type: ignore[type-abstract]
        do_play_args)
    add_path_arg(p, cwd)
    _ = p.add_argument(
        "--10",
        dest="force_channel_10",
        metavar="FORCE_CHANNEL_10",
        action=BooleanOptionalAction,
        default=False,
        help="remap all notes to MIDI channel 10")
    _ = p.add_argument(
        "--port",
        "-p",
        dest="port_name",
        metavar="PORT_NAME",
        type=str,
        default=None,
        help="MIDI port name")

    p = add_parser(
        parsers,
        "remap",
        "remap all notes to MIDI channel 10",
        RemapArgs,  # type: ignore[type-abstract]
        do_remap_args)
    add_path_arg(p, cwd)
    add_output_path_arg(p, cwd)

    args = parser.parse_args(argv)
    args_cls, func = cast(tuple[ArgsType, Func[Namespace]], args.handler)
    assert \
        isinstance(args, args_cls), \
        f"type of arguments {type(args)} does not conform to protocol {args_cls}"

    try:
        func(args)
    except KeyboardInterrupt:
        print(
            "\n",
            Fore.LIGHTRED_EX,
            "Operation cancelled",
            Style.RESET_ALL,
            sep="",
            file=sys.stderr)
        sys.exit(2)
    except UserError as e:
        print(Fore.LIGHTRED_EX, str(e), Style.RESET_ALL, sep="", file=sys.stderr)
        sys.exit(1)
