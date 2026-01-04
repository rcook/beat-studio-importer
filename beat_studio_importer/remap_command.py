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

# pyright: reportUnknownMemberType=false

from beat_studio_importer.user_error import UserError
from collections.abc import Iterable
from mido import MidiFile, MidiTrack
from mido.messages import BaseMessage
from pathlib import Path
from typing import cast


def do_remap(path: Path, output_path: Path) -> None:
    if not path.is_file():
        raise UserError(f"Path {path} not found")
    if output_path.is_file():
        raise UserError(f"Output path {output_path} already exists")

    file = MidiFile(path)

    for track in cast(Iterable[MidiTrack], file.tracks):
        for message in cast(Iterable[BaseMessage], track):
            if hasattr(message, "channel"):
                message.channel = 9

    file.save(output_path)
