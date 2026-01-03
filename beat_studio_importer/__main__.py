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

# pyright: reportAny=false
# pyright: reportPrivateUsage=false

from argparse import _SubParsersAction, ArgumentParser, BooleanOptionalAction, Namespace
from beat_studio_importer.import_command import do_import
from beat_studio_importer.info_command import do_info
from beat_studio_importer.misc import BeatStudioTempo, MidiChannel, RegionId
from beat_studio_importer.note_name_map import NoteNameMap
from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.play_command import do_play
from beat_studio_importer.typing_util import checked_cast
from beat_studio_importer.user_error import UserError
from colorama import Fore, Style
from pathlib import Path
import sys


def do_import_args(args: Namespace) -> None:
    note_name_map = None \
        if args.note_name_path is None \
        else NoteNameMap.load(checked_cast(Path, args.note_name_path))

    temp0 = checked_cast(int, args.channel, optional=True)
    channel = None if temp0 is None else MidiChannel(temp0)

    temp1 = checked_cast(int, args.region, optional=True)
    region_id = None if temp1 is None else RegionId(temp1)

    quantize = NoteValue.from_int(checked_cast(int, args.quantize))

    temp2 = checked_cast(int, args.override_tempo, optional=True)
    override_tempo = None if temp2 is None else BeatStudioTempo(temp2)

    do_import(
        path=checked_cast(Path, args.path),
        note_name_map=note_name_map,
        channel=channel,
        region_id=region_id,
        quantize=quantize,
        name=checked_cast(str, args.name, optional=True),
        override_tempo=override_tempo,
        repeat=checked_cast(int, args.repeat, optional=True),
        add=checked_cast(bool, args.add))


def do_info_args(args: Namespace) -> None:
    do_info(path=checked_cast(Path, args.path, optional=True))


def do_play_args(args: Namespace) -> None:
    temp0 = checked_cast(bool, args.force_channel_10, optional=True)
    force_channel_10 = temp0 or False

    port_name = checked_cast(str, args.port_name, optional=True)

    do_play(
        path=checked_cast(Path, args.path),
        port_name=port_name,
        force_channel_10=force_channel_10)


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
    def add_parser(parsers: "_SubParsersAction[ArgumentParser]", name: str, help: str) -> ArgumentParser:
        return parsers.add_parser(
            name=name,
            help=help,
            description=help[0].upper() + help[1:])

    parser = ArgumentParser(
        prog="beat-studio-importer",
        description="Import patterns from MIDI files into Beat Studio patterns.beat file")
    parsers = parser.add_subparsers(required=True)

    p = add_parser(parsers, "import", "import pattern from MIDI file")
    p.set_defaults(func=do_import_args)
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
        choices=sorted(member.value[0] for member in NoteValue),
        default=NoteValue.SIXTEENTH.value[0],
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
        type=int,
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

    p = add_parser(
        parsers,
        "info",
        "show information about Beat Studio profile and (optionally) contents of a MIDI file")
    p.set_defaults(func=do_info_args)
    add_path_arg(p, cwd, optional=True)

    p = add_parser(parsers, "play", "play MIDI file")
    p.set_defaults(func=do_play_args)
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

    args = parser.parse_args(argv)
    result: object = None
    try:
        result = args.func(args)
    except KeyboardInterrupt:
        print("\n",
              Fore.LIGHTRED_EX,
              "Operation cancelled",
              Style.RESET_ALL,
              sep="",
              file=sys.stderr)
        sys.exit(2)
    except UserError as e:
        print(Fore.LIGHTRED_EX, str(e), Style.RESET_ALL, sep="", file=sys.stderr)
        sys.exit(1)

    if result is None:
        pass
    else:
        raise NotImplementedError()
