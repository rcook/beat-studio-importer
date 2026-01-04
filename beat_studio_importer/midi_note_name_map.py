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

from beat_studio_importer.midi_note_name import MidiNoteName
from beat_studio_importer.misc import MidiNote
from dataclasses import dataclass
from pathlib import Path
from typing import Self, cast
import yaml


@dataclass(frozen=True)
class MidiNoteNameMap:
    path: Path | None
    name: str
    notes: dict[MidiNote, MidiNoteName]

    @classmethod
    def load(cls: type[Self], path: Path) -> Self:
        with path.open("rt") as f:
            obj = cast(
                dict[str, object],
                yaml.load(stream=f, Loader=yaml.SafeLoader))
        return cls(
            path=path,
            name=cast(str, obj["name"]),
            notes={
                MidiNote(note): MidiNoteName.parse(s)
                for note, s in cast(dict[int, str], obj["notes"]).items()
            })

    def __getitem__(self, key: MidiNote) -> MidiNoteName:
        return self.notes[key]

    def get(self, key: MidiNote) -> MidiNoteName | None:
        return self.notes.get(key)

    def save_as(self, path: Path) -> None:
        with path.open("wt") as f:
            yaml.dump({
                "name": self.name,
                "notes": {
                    k: v.display
                    for k, v in self.notes.items()
                }
            }, stream=f)


DEFAULT_MIDI_NOTE_NAME_MAP: MidiNoteNameMap = MidiNoteNameMap(
    path=None,
    name="(default)",
    notes={
        x.midi_note: x
        for x in MidiNoteName
    })
