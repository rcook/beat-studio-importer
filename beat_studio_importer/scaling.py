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
