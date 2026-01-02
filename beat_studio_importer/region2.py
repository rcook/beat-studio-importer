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

from beat_studio_importer.misc import Denominator, MidiTempo, Numerator, RegionId, Tick, TimeSignature2
from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.time_signature import TimeSignature
from beat_studio_importer.timeline import NoteEvent, TempoEvent, TimeSignatureEvent, Timeline
from dataclasses import dataclass
from functools import reduce
from typing import TypeVar


DEFAULT_TEMPO: MidiTempo = MidiTempo(120)
DEFAULT_TIME_SIGNATURE: TimeSignature2 = (Numerator(4), Denominator(4))


T = TypeVar("T", bound="Region2")


@dataclass(frozen=True)
class Region2:
    id: RegionId
    start_tick: Tick
    end_tick: Tick
    tempo: MidiTempo
    time_signature: TimeSignature
    notes: list[NoteEvent]

    @classmethod
    def build_all(cls: type[T], timeline: Timeline, discard_boundary_hits: bool = True) -> list[T]:
        regions: list[T] = []
        tempo = DEFAULT_TEMPO
        time_signature = DEFAULT_TIME_SIGNATURE
        start_tick = Tick(0)
        tempo_event: TempoEvent | None = None
        time_signature_event: TimeSignatureEvent | None = None
        note_events: list[NoteEvent] = []
        for event_tick, events in timeline.events:
            assert event_tick >= start_tick
            for event in events:
                match event:
                    case TempoEvent() | TimeSignatureEvent() as e:
                        if event_tick == start_tick:
                            if isinstance(e, TempoEvent):
                                assert tempo_event is None, "conflicting tempo events"
                                tempo_event = e
                            else:
                                assert time_signature_event is None, "conflicting time signature events"
                                time_signature_event = e
                        else:
                            region, tempo, time_signature = cls._close_region(
                                timeline=timeline,
                                tempo=tempo,
                                time_signature=time_signature,
                                region_id=RegionId(len(regions)),
                                start_tick=start_tick,
                                end_tick=event_tick,
                                tempo_event=tempo_event,
                                time_signature_event=time_signature_event,
                                note_events=note_events,
                                discard_boundary_hits=discard_boundary_hits)
                            if region is not None:
                                regions.append(region)
                            start_tick = event_tick
                            if isinstance(e, TempoEvent):
                                tempo_event = e
                                time_signature_event = None
                            else:
                                tempo_event = None
                                time_signature_event = e
                            note_events = []
                    case NoteEvent() as e: note_events.append(e)

        region, _, _ = cls._close_region(
            timeline=timeline,
            tempo=tempo,
            time_signature=time_signature,
            region_id=RegionId(len(regions)),
            start_tick=start_tick,
            end_tick=None,
            tempo_event=tempo_event,
            time_signature_event=time_signature_event,
            note_events=note_events,
            discard_boundary_hits=discard_boundary_hits)
        if region is not None:
            regions.append(region)

        return regions

    @classmethod
    def _close_region(cls: type[T], timeline: Timeline, tempo: MidiTempo, time_signature: tuple[Numerator, Denominator], region_id: RegionId, start_tick: Tick, end_tick: Tick | None, tempo_event: TempoEvent | None, time_signature_event: TimeSignatureEvent | None, note_events: list[NoteEvent], discard_boundary_hits: bool) -> tuple[T | None, MidiTempo, TimeSignature2]:
        def reduce_func(end_tick: Tick, note_event: NoteEvent) -> Tick:
            assert note_event.tick >= end_tick
            return max(end_tick, note_event.tick)

        if tempo_event is None and time_signature_event is None and len(note_events) == 0:
            return None, tempo, time_signature

        if tempo_event is None:
            temp_tempo = tempo
        else:
            assert tempo_event.tick == start_tick
            temp_tempo = tempo_event.tempo

        if time_signature_event is None:
            temp_time_signature = time_signature
        else:
            assert time_signature_event.tick == start_tick
            temp_time_signature = time_signature_event.numerator, time_signature_event.denominator

        temp = TimeSignature(
            numerator=temp_time_signature[0],
            denominator=NoteValue.from_int(temp_time_signature[1]))

        if end_tick is None:
            end_tick = reduce(reduce_func, note_events, start_tick)

        ticks_per_bar = temp.ticks_per_bar(timeline.ticks_per_beat)

        # Handle note hit on boundary
        bar_count, r = divmod(end_tick - start_tick, ticks_per_bar)
        assert bar_count >= 0 and r >= 0
        if r == 0 and discard_boundary_hits:
            _ = note_events.pop()
        else:
            bar_count += 1

        end_tick = Tick(start_tick + bar_count * ticks_per_bar)

        region = cls(
            id=region_id,
            start_tick=start_tick,
            end_tick=end_tick,
            tempo=temp_tempo,
            time_signature=temp,
            notes=note_events)
        return region, temp_tempo, temp_time_signature
