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
from beat_studio_importer.beat_studio_pattern import BeatStudioPattern, Hits
from beat_studio_importer.beat_studio_velocity import BeatStudioVelocity
from beat_studio_importer.descriptor import Descriptor
from beat_studio_importer.misc import BeatStudioTempo, Bpm, MidiTempo, Numerator, Qpm, RegionId, Tick
from beat_studio_importer.note_name_map import NoteNameMap
from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.tempo_util import midi_tempo_to_qpm
from beat_studio_importer.time_signature import TimeSignature
from beat_studio_importer.timeline import NoteEvent, TempoEvent, TimeSignatureEvent, Timeline
from dataclasses import dataclass
from functools import cached_property, reduce
from typing import Self

from beat_studio_importer.user_error import UserError


DEFAULT_TEMPO: MidiTempo = MidiTempo(120)
DEFAULT_TIME_SIGNATURE: TimeSignature = TimeSignature(
    numerator=Numerator(4),
    denominator=NoteValue.QUARTER)


TEMPO_RANGE: tuple[BeatStudioTempo, BeatStudioTempo] = (
    BeatStudioTempo(60),
    BeatStudioTempo(200)
)
STEP_COUNT_RANGE: tuple[int, int] = (16, 2048)


@dataclass(frozen=True)
class Region:
    id: RegionId
    ticks_per_beat: int
    start_tick: Tick
    end_tick: Tick
    tempo: MidiTempo
    time_signature: TimeSignature
    notes: list[NoteEvent]
    bar_count: int

    @classmethod
    def build_all(cls: type[Self], timeline: Timeline, discard_boundary_hits: bool = True) -> list[Self]:
        regions: list[Self] = []
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
                                region_id=RegionId(len(regions) + 1),
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
            region_id=RegionId(len(regions) + 1),
            start_tick=start_tick,
            end_tick=None,
            tempo_event=tempo_event,
            time_signature_event=time_signature_event,
            note_events=note_events,
            discard_boundary_hits=discard_boundary_hits)
        if region is not None:
            regions.append(region)

        return regions

    @cached_property
    def descriptor(self) -> Descriptor:
        return Descriptor(
            name=None,
            description=f"{self.start_tick}-{self.end_tick}: {self.qpm:.1f}qpm, {self.bpm:.1f}bpm, {self.time_signature}, {self.bar_count} bars")

    # Tempo as quarter notes per minute
    @cached_property
    def qpm(self) -> Qpm:
        return midi_tempo_to_qpm(self.tempo)

    # Tempo as beats (pulses) per minute
    @cached_property
    def bpm(self) -> Bpm:
        return self.time_signature.pulse.midi_tempo_to_bpm(self.tempo)

    def render(self, name: str, note_name_map: NoteNameMap, quantize: NoteValue, override_tempo: BeatStudioTempo | None = None, repeat: int | None = None) -> BeatStudioPattern:
        # What is Beat Studio tempo? QPM, BPM or something else?
        # Assume it's supposed to be QPM for now
        tempo = BeatStudioTempo(round(midi_tempo_to_qpm(self.tempo))) \
            if override_tempo is None \
            else override_tempo
        if not (TEMPO_RANGE[0] <= tempo <= TEMPO_RANGE[1]):
            # TBD: Move user-facing exceptions out of here!
            raise UserError(
                f"Tempo {tempo} is outside allowed range {TEMPO_RANGE}: specify a valid tempo using --tempo")

        ticks_per_step, r = divmod(self.ticks_per_beat * 4, quantize.value[0])
        assert r == 0

        tick_count = self.end_tick - self.start_tick
        step_count, r = divmod(tick_count, ticks_per_step)
        assert r == 0

        total_step_count = step_count if repeat is None else step_count * repeat

        if not (STEP_COUNT_RANGE[0] <= total_step_count <= STEP_COUNT_RANGE[1]):
            # TBD: Move user-facing exceptions out of here!
            raise UserError(
                f"Number of steps {total_step_count} is outside allowed range {STEP_COUNT_RANGE}: use a shorter pattern or specify repetitions using --repeat")

        all_hits: Hits = {
            member: [None] * total_step_count
            for member in BeatStudioNoteName
        }

        for e in self.notes:
            step, r = divmod(e.tick - self.start_tick, ticks_per_step)
            assert r == 0
            note_name = note_name_map[e.note]
            _, key, = note_name.value
            hits = all_hits[key]
            velocity = BeatStudioVelocity.from_midi_velocity(e.velocity)
            hits[step] = velocity
            if repeat is None:
                hits[step] = velocity
            else:
                for i in range(repeat):
                    hits[step + i * step_count] = velocity

        return BeatStudioPattern(
            name=name,
            tempo=tempo,
            time_signature=self.time_signature,
            quantize=quantize,
            step_count=total_step_count,
            hits=all_hits)

    @classmethod
    def _close_region(cls: type[Self], timeline: Timeline, tempo: MidiTempo, time_signature: TimeSignature, region_id: RegionId, start_tick: Tick, end_tick: Tick | None, tempo_event: TempoEvent | None, time_signature_event: TimeSignatureEvent | None, note_events: list[NoteEvent], discard_boundary_hits: bool) -> tuple[Self | None, MidiTempo, TimeSignature]:
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
            temp_time_signature = TimeSignature(
                numerator=time_signature_event.numerator,
                denominator=NoteValue.from_int(time_signature_event.denominator))

        if end_tick is None:
            end_tick = reduce(reduce_func, note_events, start_tick)

        ticks_per_bar = temp_time_signature.ticks_per_bar(
            timeline.ticks_per_beat)

        # Handle note hit on boundary
        if len(note_events) > 0:
            bar_count, r = divmod(end_tick - start_tick, ticks_per_bar)
            assert bar_count >= 0 and r >= 0
            if r == 0 and discard_boundary_hits:
                e = note_events[-1]
                assert e.tick <= end_tick
                if e.tick >= end_tick:
                    e = note_events.pop()
            else:
                bar_count += 1
        else:
            bar_count = 1

        end_tick = Tick(start_tick + bar_count * ticks_per_bar)

        region = cls(
            id=region_id,
            ticks_per_beat=timeline.ticks_per_beat,
            start_tick=start_tick,
            end_tick=end_tick,
            tempo=temp_tempo,
            time_signature=temp_time_signature,
            notes=note_events,
            bar_count=bar_count)
        return region, temp_tempo, temp_time_signature
