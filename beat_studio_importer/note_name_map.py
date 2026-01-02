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

from beat_studio_importer.note_name import NoteName
from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar, cast
import yaml


T = TypeVar("T", bound="NoteNameMap")


@dataclass(frozen=True)
class NoteNameMap:
    name: str
    notes: dict[int, NoteName]

    @classmethod
    def load(cls: type[T], path: Path) -> T:
        with path.open("rt") as f:
            obj = cast(
                dict[str, object],
                yaml.load(stream=f, Loader=yaml.SafeLoader))
        return cls(
            name=cast(str, obj["name"]),
            notes={
                k: NoteName[v.upper()]
                for k, v in cast(dict[int, str], obj["notes"]).items()
            })

    def __getitem__(self, key: int) -> NoteName:
        return self.notes[key]

    def save(self, path: Path) -> None:
        with path.open("wt") as f:
            yaml.dump({
                "name": self.name,
                "notes": {
                    k: v.name.lower()
                    for k, v in self.notes.items()
                }
            }, stream=f)


DEFAULT_NOTE_NAME_MAP: NoteNameMap = NoteNameMap.load(
    Path(__file__).parent.parent / "note-maps/general-midi-drums.notemap")
