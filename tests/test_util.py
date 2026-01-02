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

from beat_studio_importer.util import downscale


class TestDownscale:
    def test_basics(self) -> None:
        def call_downscale(value: int) -> int:
            return downscale(value, range(0, 30), range(0, 10))

        assert call_downscale(0) == 0
        assert call_downscale(1) == 0
        assert call_downscale(2) == 1
        assert call_downscale(3) == 1
        assert call_downscale(4) == 1
        assert call_downscale(5) == 2
        assert call_downscale(6) == 2
        assert call_downscale(7) == 2
        assert call_downscale(8) == 2
        assert call_downscale(9) == 3
        assert call_downscale(10) == 3
        assert call_downscale(11) == 3
        assert call_downscale(12) == 4
        assert call_downscale(13) == 4
        assert call_downscale(14) == 4
        assert call_downscale(15) == 5
        assert call_downscale(16) == 5
        assert call_downscale(17) == 5
        assert call_downscale(18) == 6
        assert call_downscale(19) == 6
        assert call_downscale(20) == 6
        assert call_downscale(21) == 7
        assert call_downscale(22) == 7
        assert call_downscale(23) == 7
        assert call_downscale(24) == 7
        assert call_downscale(25) == 8
        assert call_downscale(26) == 8
        assert call_downscale(27) == 8
        assert call_downscale(28) == 9
        assert call_downscale(29) == 9
