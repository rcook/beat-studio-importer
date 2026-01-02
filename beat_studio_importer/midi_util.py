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

from beat_studio_importer.table import Table
from beat_studio_importer.ui import cprint, print_key_value
from collections.abc import Iterable
from colorama import Fore
from mido import MidiFile, MidiTrack
from mido.messages import BaseMessage
from pathlib import Path
from typing import cast


def summarize_midi_file(file: MidiFile) -> None:
    midi_channels: set[int] = set()
    message_counts: dict[str, int] = {}

    for track in cast(Iterable[MidiTrack], file.tracks):
        for m in cast(Iterable[BaseMessage], track):
            # autopep8: off
            message_type = cast(str, m.type) # pyright: ignore[reportAttributeAccessIssue]
            # autopep8: on
            count = message_counts.get(message_type)
            if count is None:
                message_counts[message_type] = 1
            else:
                message_counts[message_type] += 1
            value = cast(int | None, getattr(m, "channel", None))
            if value is not None:
                midi_channel = value + 1
                midi_channels.add(midi_channel)

    print_key_value("File", cast(Path, file.filename))
    print_key_value("Ticks per beat", file.ticks_per_beat)

    cprint(Fore.LIGHTBLUE_EX, "Tracks:")
    for track_name in sorted(cast(str, t.name) for t in cast(Iterable[MidiTrack], file.tracks)):
        cprint("  ", Fore.LIGHTCYAN_EX, track_name)

    cprint(Fore.LIGHTBLUE_EX, "MIDI channels:")
    for value in sorted(midi_channels):
        cprint("  ", Fore.LIGHTCYAN_EX, value)

    with Table(("MIDI message", Fore.LIGHTYELLOW_EX, "{}", Fore.LIGHTBLUE_EX), ("count", Fore.LIGHTYELLOW_EX, "{:>5}", Fore.LIGHTCYAN_EX), column_sep="  ") as table:
        for message_type in sorted(message_counts.keys()):
            table.add_row(message_type, message_counts[message_type])
        table.print()
