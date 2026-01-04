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

from beat_studio_importer.ui import cprint, print_key_value
from beat_studio_importer.user_error import UserError
from collections.abc import Generator, Iterable
from colorama import Fore
from contextlib import ExitStack, contextmanager
from mido import MidiFile
from mido.messages import BaseMessage
from mido.ports import BaseOutput
from pathlib import Path
from typing import cast
import mido


@contextmanager
def open_midi_port(name: str | None) -> Generator[BaseOutput, None, None]:
    if name is not None:
        # autopep8: off
        if name not in mido.get_output_names(): # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
        # autopep8: on
            raise UserError(f"Unknown MIDI port {name}")

    with ExitStack() as stack:
        try:
            # autopep8: off
            port = stack.enter_context(
                cast(BaseOutput, mido.open_output(name))) # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            # autopep8: on
        except Exception as e:
            if type(e).__name__ != "SystemError":
                raise
            if name is None:
                raise UserError(
                    f"Could not open default MIDI output port: perhaps it is already in use?")
            else:
                raise UserError(
                    f"Could not open MIDI output port {name}: perhaps it is already in use?")
        yield port


def do_play(path: Path, port_name: str | None = None, force_channel_10: bool = True) -> None:
    with open_midi_port(port_name) as port:
        print_key_value("File", path)
        print_key_value("MIDI port", cast(str, port.name))

        if force_channel_10:
            cprint(Fore.LIGHTBLUE_EX, "Will remap all notes to MIDI channel 10")

        file = MidiFile(path)
        # autopep8: off
        for message in cast(Iterable[BaseMessage], file.play()): # pyright: ignore[reportUnknownMemberType]
        # autopep8: on
            if force_channel_10:
                if hasattr(message, "channel"):
                    message.channel = 9
            # autopep8: off
            port.send(message) # pyright: ignore[reportUnknownMemberType]
            # autopep8: on
