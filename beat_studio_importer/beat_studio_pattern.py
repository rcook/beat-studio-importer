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

from beat_studio_importer.beat_studio_note_name import BeatStudioNoteName
from beat_studio_importer.note import Velocity
from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.time_signature import TimeSignature
from beat_studio_importer.util import downscale_velocity, midi_tempo_to_qpm
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeVar


if TYPE_CHECKING:
    from _typeshed import SupportsWrite


T = TypeVar("T", bound="BeatStudioPattern")


type Hits = dict[BeatStudioNoteName, list[Velocity | None]]


@dataclass(frozen=True)
class BeatStudioPattern:
    name: str
    tempo: int
    time_signature: TimeSignature
    quantize: NoteValue
    steps: int
    hits: Hits

    def print(self, file: "SupportsWrite[str] | None" = None, override_tempo: int | None = None) -> None:
        print(self._make_header(override_tempo=override_tempo), file=file)
        temp = list(map(lambda n: (n, n.value), self.hits.keys()))
        note_names = sorted(temp, key=lambda p: p[1])
        width = max(map(lambda p: len(p[1]), temp))
        for note_name, label in note_names:
            hits = self.hits[note_name]
            hit_str = "".join(map(self.__class__._velocity_char, hits))
            print(f"{label:<{width}}: {hit_str}", file=file)

    @staticmethod
    def _velocity_char(velocity: Velocity | None) -> str:
        return "." if velocity is None else str(downscale_velocity(velocity))

    def _make_header(self, override_tempo: int | None) -> str:
        if not all(map(lambda c: c.isprintable(), self.name)):
            raise ValueError(f"Invalid pattern name {self.name}")

        encoded_name = self.name.replace("\"", "\\\"")
        qpm = round(midi_tempo_to_qpm(self.tempo)) \
            if override_tempo is None \
            else override_tempo
        return f"[\"{encoded_name}\" - {self.steps} - {qpm} - {self.quantize.value[0]} - {self.time_signature}]"
