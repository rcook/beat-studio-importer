from beat_studio_importer.misc import BeatStudioTempo, Numerator
from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.time_signature import TimeSignature


PROGRAM_NAME: str = "beat-studio-importer"

PROGRAM_URL: str = "https://github.com/rcook/beat-studio-importer"

BEAT_STUDIO_TEMPO_RANGE: tuple[BeatStudioTempo, BeatStudioTempo] = (
    BeatStudioTempo(60),
    BeatStudioTempo(200)
)

BEAT_STUDIO_STEP_COUNT_RANGE: tuple[int, int] = (4, 8192)

BEAT_STUDIO_DEFAULT_TIME_SIGNATURE: TimeSignature = TimeSignature(
    Numerator(4),
    NoteValue.QUARTER)
