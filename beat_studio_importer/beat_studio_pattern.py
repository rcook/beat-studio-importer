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
from beat_studio_importer.beat_studio_tempo import BeatStudioTempo
from beat_studio_importer.beat_studio_velocity import BeatStudioVelocity
from beat_studio_importer.constants import BEAT_STUDIO_DEFAULT_TIME_SIGNATURE
from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.time_signature import Numerator, TimeSignature
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Self


if TYPE_CHECKING:
    from _typeshed import SupportsWrite


type Hits = dict[BeatStudioNoteName, list[BeatStudioVelocity | None]]


@dataclass(frozen=True)
class BeatStudioPattern:
    name: str
    tempo: BeatStudioTempo
    time_signature: TimeSignature
    quantum: NoteValue
    step_count: int
    hits: Hits
    is_empty: bool

    @classmethod
    def load(cls: type[Self], path: Path) -> list[Self]:
        with path.open("rt") as f:
            lines = f.readlines()

        patterns: list[Self] = []
        header: str | None = None
        pattern_lines: list[str] = []
        for line in lines:
            s = line.strip()
            if s.startswith("#"):
                # Skip comment
                continue
            if len(s) == 0:
                # Skip blank line
                continue

            is_header = s.startswith("[") and s.endswith("]")
            if is_header:
                if header is None:
                    assert len(pattern_lines) == 0
                    header = s
                else:
                    patterns.append(cls.read(header, pattern_lines))
                    header = s
                    pattern_lines.clear()
            else:
                pattern_lines.append(s)

        if header is not None:
            patterns.append(cls.read(header, pattern_lines))
        return patterns

    @classmethod
    def parse(cls: type[Self], s: str) -> Self:
        header, *lines = [
            line for line in [
                line.strip()
                for line in s.splitlines()
            ] if len(line) > 0
        ]
        return cls.read(header, lines)

    @classmethod
    def read(cls: type[Self], header: str, lines: list[str]) -> Self:
        def translate_hit_char(c: str) -> BeatStudioVelocity | None:
            return None if c == "." else BeatStudioVelocity(int(c))

        if not header.startswith("[\"") or not header.endswith("]"):
            raise ValueError(f"Invalid header {header}: brackets not found")

        s = header[2:-1]

        idx = s.find("\"")
        if idx == -1:
            raise ValueError(f"Invalid header {header}: no name found")

        encoded_name = s[:idx]
        name = encoded_name.replace("\\\"", "\"")

        parts = list(filter(
            lambda s: len(s) > 0,
            map(lambda s: s.strip(), s[idx + 1:].split("-"))))
        part_count = len(parts)

        if not (3 <= part_count <= 4):
            raise ValueError(
                f"Invalid header {header}: unexpected number of values")

        step_count = int(parts[0])
        tempo = BeatStudioTempo(int(parts[1]))
        quantum = NoteValue.from_int(int(parts[2]))

        if part_count > 3:
            parts = parts[3].split("/")
            if len(parts) != 2:
                raise ValueError(
                    f"Invalid header {header}: invalid time signature")

            time_signature = TimeSignature(
                numerator=Numerator(int(parts[0])),
                denominator=NoteValue.from_int(int(parts[1])))
        else:
            time_signature = BEAT_STUDIO_DEFAULT_TIME_SIGNATURE

        hits: Hits = {}

        is_empty = True

        for line in lines:
            parts = line.split(":")
            if len(parts) != 2:
                raise ValueError(f"Invalid pattern {line}: invalid format")
            note_name = BeatStudioNoteName.parse(parts[0].strip())
            s = parts[1].strip()
            if len(s) != step_count:
                raise ValueError(f"Invalid pattern {line}: invalid step count")

            hits[note_name] = [translate_hit_char(c) for c in s]
            is_empty = is_empty and len(s.strip(".")) == 0

        return cls(
            name=name,
            tempo=tempo,
            time_signature=time_signature,
            quantum=quantum,
            step_count=step_count,
            hits=hits,
            is_empty=is_empty)

    def print(self, file: "SupportsWrite[str] | None" = None) -> None:
        print(self._make_header(), file=file)
        temp = list(map(lambda n: (n, n.display), self.hits.keys()))
        note_names = sorted(temp, key=lambda p: p[1])
        width = max(map(lambda p: len(p[1]), temp))
        for note_name, label in note_names:
            hits = self.hits[note_name]
            hit_str = "".join(map(self.__class__._velocity_char, hits))
            print(f"{label:<{width}}: {hit_str}", file=file)

    @staticmethod
    def _velocity_char(velocity: BeatStudioVelocity | None) -> str:
        return "." if velocity is None else str(velocity)

    def _make_header(self) -> str:
        if not all(map(lambda c: c.isprintable(), self.name)):
            raise ValueError(f"Invalid pattern name {self.name}")

        encoded_name = self.name.replace("\"", "\\\"")
        return f"[\"{encoded_name}\" - {self.step_count} - {self.tempo} - {self.quantum.int_value} - {self.time_signature}]"
