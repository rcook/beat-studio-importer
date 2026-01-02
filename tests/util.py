import math


def is_close_tempo(expected: int, actual: float) -> bool:
    return math.isclose(expected, actual, rel_tol=1e-6)
