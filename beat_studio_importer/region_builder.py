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

# pyright: reportAttributeAccessIssue=false

from beat_studio_importer.note import Note
from beat_studio_importer.time_signature import DEFAULT_TIME_SIGNATURE, TimeSignature
from collections.abc import Iterable
from dataclasses import dataclass, field
from mido import MetaMessage, MidiTrack
from mido.messages import BaseMessage
from typing import cast


DEFAULT_TEMPO: int = 120


type Tick = int


@dataclass(frozen=False)
class RegionBuilder:
    start_tick: Tick
    end_tick: Tick | None = None
    bars: int | None = None
    tempo: int | None = None
    time_signature: TimeSignature | None = None
    notes: list[tuple[Tick, Note]] = field(default_factory=list)

    @staticmethod
    def from_midi_messages(metadata_track: MidiTrack, ticks_per_beat: int) -> "list[RegionBuilder]":
        tick = 0
        regions: list[RegionBuilder] = []

        region = RegionBuilder(start_tick=tick)
        regions.append(region)

        for m in cast(Iterable[BaseMessage], metadata_track):
            delta = cast(int, m.time)
            assert delta >= 0
            tick += delta

            if delta > 0:
                region.end_tick = tick
                region = RegionBuilder(start_tick=tick)
                regions.append(region)

            match cast(str, m.type):
                case "set_tempo":
                    tempo = cast(int, m.tempo)
                    if region.tempo is not None:
                        raise RuntimeError(
                            "Invalid region in MIDI file (more than one tempo message encountered)")
                    region.tempo = tempo
                case "time_signature":
                    time_signature = TimeSignature.from_midi_message(
                        cast(MetaMessage, m))
                    if region.time_signature is not None:
                        raise RuntimeError(
                            "Invalid region in MIDI file (more than one time signature message encountered)")
                    region.time_signature = time_signature
                case _: pass

        current_tempo = DEFAULT_TEMPO
        current_time_signature = DEFAULT_TIME_SIGNATURE

        for region in regions:
            if region.tempo is None:
                region.tempo = current_tempo
            else:
                current_tempo = region.tempo

            if region.time_signature is None:
                region.time_signature = current_time_signature
            else:
                current_time_signature = region.time_signature

            if region.end_tick is not None:
                ticks = region.end_tick - region.start_tick
                ticks_per_bar = current_time_signature.ticks_per_bar(
                    ticks_per_beat)
                bars, r = divmod(ticks, ticks_per_bar)
                if r != 0:
                    raise RuntimeError("Region is not whole number of bars")
                region.bars = bars

        return regions
