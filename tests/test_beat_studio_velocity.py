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

from beat_studio_importer.beat_studio_velocity import BeatStudioVelocity
from beat_studio_importer.misc import MidiVelocity
import pytest


class TestBeatStudioVelocity:
    def test_basics(self) -> None:
        assert BeatStudioVelocity.from_midi_velocity(MidiVelocity(1)) == 1
        assert BeatStudioVelocity.from_midi_velocity(MidiVelocity(127)) == 9

    def test_zero_velocity(self) -> None:
        with pytest.raises(ValueError):
            _ = BeatStudioVelocity.from_midi_velocity(MidiVelocity(0))

    @pytest.mark.parametrize("velocity, expected", [
        (MidiVelocity(1), BeatStudioVelocity(1)),
        (MidiVelocity(2), BeatStudioVelocity(1)),
        (MidiVelocity(3), BeatStudioVelocity(1)),
        (MidiVelocity(4), BeatStudioVelocity(1)),
        (MidiVelocity(5), BeatStudioVelocity(1)),
        (MidiVelocity(6), BeatStudioVelocity(1)),
        (MidiVelocity(7), BeatStudioVelocity(1)),
        (MidiVelocity(8), BeatStudioVelocity(1)),
        (MidiVelocity(9), BeatStudioVelocity(1)),
        (MidiVelocity(10), BeatStudioVelocity(1)),
        (MidiVelocity(11), BeatStudioVelocity(1)),
        (MidiVelocity(12), BeatStudioVelocity(1)),
        (MidiVelocity(13), BeatStudioVelocity(1)),
        (MidiVelocity(14), BeatStudioVelocity(1)),
        (MidiVelocity(15), BeatStudioVelocity(2)),
        (MidiVelocity(16), BeatStudioVelocity(2)),
        (MidiVelocity(17), BeatStudioVelocity(2)),
        (MidiVelocity(18), BeatStudioVelocity(2)),
        (MidiVelocity(19), BeatStudioVelocity(2)),
        (MidiVelocity(20), BeatStudioVelocity(2)),
        (MidiVelocity(21), BeatStudioVelocity(2)),
        (MidiVelocity(22), BeatStudioVelocity(2)),
        (MidiVelocity(23), BeatStudioVelocity(2)),
        (MidiVelocity(24), BeatStudioVelocity(2)),
        (MidiVelocity(25), BeatStudioVelocity(2)),
        (MidiVelocity(26), BeatStudioVelocity(2)),
        (MidiVelocity(27), BeatStudioVelocity(2)),
        (MidiVelocity(28), BeatStudioVelocity(2)),
        (MidiVelocity(29), BeatStudioVelocity(3)),
        (MidiVelocity(30), BeatStudioVelocity(3)),
        (MidiVelocity(31), BeatStudioVelocity(3)),
        (MidiVelocity(32), BeatStudioVelocity(3)),
        (MidiVelocity(33), BeatStudioVelocity(3)),
        (MidiVelocity(34), BeatStudioVelocity(3)),
        (MidiVelocity(35), BeatStudioVelocity(3)),
        (MidiVelocity(36), BeatStudioVelocity(3)),
        (MidiVelocity(37), BeatStudioVelocity(3)),
        (MidiVelocity(38), BeatStudioVelocity(3)),
        (MidiVelocity(39), BeatStudioVelocity(3)),
        (MidiVelocity(40), BeatStudioVelocity(3)),
        (MidiVelocity(41), BeatStudioVelocity(3)),
        (MidiVelocity(42), BeatStudioVelocity(3)),
        (MidiVelocity(43), BeatStudioVelocity(4)),
        (MidiVelocity(44), BeatStudioVelocity(4)),
        (MidiVelocity(45), BeatStudioVelocity(4)),
        (MidiVelocity(46), BeatStudioVelocity(4)),
        (MidiVelocity(47), BeatStudioVelocity(4)),
        (MidiVelocity(48), BeatStudioVelocity(4)),
        (MidiVelocity(49), BeatStudioVelocity(4)),
        (MidiVelocity(50), BeatStudioVelocity(4)),
        (MidiVelocity(51), BeatStudioVelocity(4)),
        (MidiVelocity(52), BeatStudioVelocity(4)),
        (MidiVelocity(53), BeatStudioVelocity(4)),
        (MidiVelocity(54), BeatStudioVelocity(4)),
        (MidiVelocity(55), BeatStudioVelocity(4)),
        (MidiVelocity(56), BeatStudioVelocity(4)),
        (MidiVelocity(57), BeatStudioVelocity(5)),
        (MidiVelocity(58), BeatStudioVelocity(5)),
        (MidiVelocity(59), BeatStudioVelocity(5)),
        (MidiVelocity(60), BeatStudioVelocity(5)),
        (MidiVelocity(61), BeatStudioVelocity(5)),
        (MidiVelocity(62), BeatStudioVelocity(5)),
        (MidiVelocity(63), BeatStudioVelocity(5)),
        (MidiVelocity(64), BeatStudioVelocity(5)),
        (MidiVelocity(65), BeatStudioVelocity(5)),
        (MidiVelocity(66), BeatStudioVelocity(5)),
        (MidiVelocity(67), BeatStudioVelocity(5)),
        (MidiVelocity(68), BeatStudioVelocity(5)),
        (MidiVelocity(69), BeatStudioVelocity(5)),
        (MidiVelocity(70), BeatStudioVelocity(5)),
        (MidiVelocity(71), BeatStudioVelocity(6)),
        (MidiVelocity(72), BeatStudioVelocity(6)),
        (MidiVelocity(73), BeatStudioVelocity(6)),
        (MidiVelocity(74), BeatStudioVelocity(6)),
        (MidiVelocity(75), BeatStudioVelocity(6)),
        (MidiVelocity(76), BeatStudioVelocity(6)),
        (MidiVelocity(77), BeatStudioVelocity(6)),
        (MidiVelocity(78), BeatStudioVelocity(6)),
        (MidiVelocity(79), BeatStudioVelocity(6)),
        (MidiVelocity(80), BeatStudioVelocity(6)),
        (MidiVelocity(81), BeatStudioVelocity(6)),
        (MidiVelocity(82), BeatStudioVelocity(6)),
        (MidiVelocity(83), BeatStudioVelocity(6)),
        (MidiVelocity(84), BeatStudioVelocity(6)),
        (MidiVelocity(85), BeatStudioVelocity(7)),
        (MidiVelocity(86), BeatStudioVelocity(7)),
        (MidiVelocity(87), BeatStudioVelocity(7)),
        (MidiVelocity(88), BeatStudioVelocity(7)),
        (MidiVelocity(89), BeatStudioVelocity(7)),
        (MidiVelocity(90), BeatStudioVelocity(7)),
        (MidiVelocity(91), BeatStudioVelocity(7)),
        (MidiVelocity(92), BeatStudioVelocity(7)),
        (MidiVelocity(93), BeatStudioVelocity(7)),
        (MidiVelocity(94), BeatStudioVelocity(7)),
        (MidiVelocity(95), BeatStudioVelocity(7)),
        (MidiVelocity(96), BeatStudioVelocity(7)),
        (MidiVelocity(97), BeatStudioVelocity(7)),
        (MidiVelocity(98), BeatStudioVelocity(7)),
        (MidiVelocity(99), BeatStudioVelocity(8)),
        (MidiVelocity(100), BeatStudioVelocity(8)),
        (MidiVelocity(101), BeatStudioVelocity(8)),
        (MidiVelocity(102), BeatStudioVelocity(8)),
        (MidiVelocity(103), BeatStudioVelocity(8)),
        (MidiVelocity(104), BeatStudioVelocity(8)),
        (MidiVelocity(105), BeatStudioVelocity(8)),
        (MidiVelocity(106), BeatStudioVelocity(8)),
        (MidiVelocity(107), BeatStudioVelocity(8)),
        (MidiVelocity(108), BeatStudioVelocity(8)),
        (MidiVelocity(109), BeatStudioVelocity(8)),
        (MidiVelocity(110), BeatStudioVelocity(8)),
        (MidiVelocity(111), BeatStudioVelocity(8)),
        (MidiVelocity(112), BeatStudioVelocity(8)),
        (MidiVelocity(113), BeatStudioVelocity(9)),
        (MidiVelocity(114), BeatStudioVelocity(9)),
        (MidiVelocity(115), BeatStudioVelocity(9)),
        (MidiVelocity(116), BeatStudioVelocity(9)),
        (MidiVelocity(117), BeatStudioVelocity(9)),
        (MidiVelocity(118), BeatStudioVelocity(9)),
        (MidiVelocity(119), BeatStudioVelocity(9)),
        (MidiVelocity(120), BeatStudioVelocity(9)),
        (MidiVelocity(121), BeatStudioVelocity(9)),
        (MidiVelocity(122), BeatStudioVelocity(9)),
        (MidiVelocity(123), BeatStudioVelocity(9)),
        (MidiVelocity(124), BeatStudioVelocity(9)),
        (MidiVelocity(125), BeatStudioVelocity(9)),
        (MidiVelocity(126), BeatStudioVelocity(9)),
        (MidiVelocity(127), BeatStudioVelocity(9))
    ])
    def test_exhaustive(self, velocity: MidiVelocity, expected: BeatStudioVelocity) -> None:
        assert BeatStudioVelocity.from_midi_velocity(velocity) == expected
