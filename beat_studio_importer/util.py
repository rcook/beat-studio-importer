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

from beat_studio_importer.note import Velocity
from typing import Literal, overload


MIDI_TEMPO_BASIS: int = 60_000_000


def is_valid_scale(range: range) -> bool:
    return range.stop >= range.start and range.step == 1


def downscale(value: int, source: range, target: range) -> int:
    if not is_valid_scale(source):
        raise ValueError(f"Invalid source range {source}")
    if not is_valid_scale(target):
        raise ValueError(f"Invalid target range {target}")

    if value not in source:
        raise ValueError(f"Value {value} is outside source range {source}")

    source_size = source.stop - source.start - 1
    target_size = target.stop - target.start - 1

    scaled_value = ((value - source.start) / source_size) * \
        target_size + target.start

    return int(round(scaled_value))


def downscale_velocity(velocity: Velocity) -> int:
    return downscale(velocity, range(0, 128), range(0, 10))


# Tempo as quarter notes per minute
def midi_tempo_to_qpm(tempo: int) -> float:
    return MIDI_TEMPO_BASIS / tempo


@overload
def checked_cast[T](cls: type[T], value: object, optional: Literal[True]) -> T | None:
    raise NotImplementedError()


@overload
def checked_cast[T](cls: type[T], value: object, optional: Literal[False]) -> T:
    raise NotImplementedError()


@overload
def checked_cast[T](cls: type[T], value: object) -> T:
    raise NotImplementedError()


def checked_cast[T](cls: type[T], value: object, optional: bool = False) -> T | None:
    if optional and value is None:
        return value
    if isinstance(value, cls):
        return value
    raise AssertionError(
        f"Value {value} of type {type(value)} is not of required type {cls}")
