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

from beat_studio_importer.misc import Ppqn
from beat_studio_importer.pulse import Pulse
from enum import Enum, unique


@unique
class NoteValue(Enum):
    WHOLE = 1, Pulse.WHOLE
    HALF = 2, Pulse.HALF
    QUARTER = 4, Pulse.QUARTER
    EIGHTH = 8, Pulse.EIGHTH
    SIXTEENTH = 16, Pulse.SIXTEENTH
    THIRTY_SECOND = 32, Pulse.THIRTY_SECOND
    SIXTY_FOURTH = 64, Pulse.SIXTY_FOURTH

    @staticmethod
    def from_int(value: int) -> "NoteValue":
        for member in NoteValue:
            if member.int_value == value:
                return member
        raise ValueError(f"Invalid note value {value}")

    @property
    def int_value(self) -> int: return self.value[0]

    @property
    def pulse(self) -> Pulse: return self.value[1]

    def ticks(self, ppqn: Ppqn) -> int:
        ticks, r = divmod(ppqn * 4, self.int_value)
        assert r == 0
        return ticks
