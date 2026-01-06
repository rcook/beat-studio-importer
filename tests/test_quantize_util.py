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

from beat_studio_importer.misc import Ppqn, Tick
from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.quantize_util import quantize, round_to_base
import pytest


class TestRoundToBase:
    @pytest.mark.parametrize("value, base, expected", [
        (1, 1, 1),
        (1.0, 1, 1),
        (10, 5, 10),
        (11, 5, 10),
        (12, 5, 10),
        (13, 5, 15),
        (14, 5, 15),
        (16, 5, 15),
        (17, 5, 15),
        (18, 5, 20),
        (18.5, 5, 20),
    ])
    def test_basics(self, value: int | float, base: int, expected: int) -> None:
        result = round_to_base(value, base)
        assert isinstance(result, int)
        assert result == expected

    def test_zero_base(self) -> None:
        with pytest.raises(ZeroDivisionError):
            _ = round_to_base(1, 0)


class TestQuantize:
    @pytest.mark.parametrize("tick, ppqn, quantum, expected", [
        (Tick(239), Ppqn(960), NoteValue.SIXTEENTH, Tick(240)),
        (Tick(240), Ppqn(960), NoteValue.SIXTEENTH, Tick(240)),
        (Tick(241), Ppqn(960), NoteValue.SIXTEENTH, Tick(240)),
        (Tick(359), Ppqn(960), NoteValue.SIXTEENTH, Tick(240)),
        (Tick(360), Ppqn(960), NoteValue.SIXTEENTH, Tick(480)),
        (Tick(361), Ppqn(960), NoteValue.SIXTEENTH, Tick(480)),
        (Tick(479), Ppqn(960), NoteValue.SIXTEENTH, Tick(480)),
        (Tick(480), Ppqn(960), NoteValue.SIXTEENTH, Tick(480)),
        (Tick(481), Ppqn(960), NoteValue.SIXTEENTH, Tick(480))
    ])
    def test_basics(self, tick: Tick, ppqn: Ppqn, quantum: NoteValue, expected: Tick) -> None:
        assert quantize(tick, ppqn, quantum) == expected
