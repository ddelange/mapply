# BSD 3-Clause License
#
# Copyright (c) 2024, ddelange, <ddelange@delange.dev>
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# SPDX-License-Identifier: BSD-3-Clause
import pytest

from mapply.parallel import multiprocessing_imap


def foo(x, power):  # noqa: D103
    if not isinstance(power, float):
        msg = "To check we reraise errors from subprocesses"
        raise ValueError(msg)  # noqa: TRY004
    return pow(x, power)


def test_multiprocessing_imap(size=100, power=1.1):  # noqa:D103,PT028
    multicore_list1 = list(
        multiprocessing_imap(
            foo,
            range(size),
            power=power,
            progressbar=False,
            n_workers=size,
        ),
    )
    multicore_list2 = list(
        multiprocessing_imap(
            foo,
            range(size),
            power=power,
            progressbar=True,
            n_workers=1,
        ),
    )
    multicore_list3 = list(
        multiprocessing_imap(  # generator with unknown length
            foo,
            (i for i in range(size)),
            power=power,
            progressbar=False,
            n_workers=2,
        ),
    )

    assert multicore_list1 == multicore_list2
    assert multicore_list1 == multicore_list3
    assert multicore_list1 == [foo(x, power=power) for x in range(size)]
    with pytest.raises(ValueError, match="reraise"):
        # hit with ProcessPool
        list(
            multiprocessing_imap(
                foo,
                range(size),
                power=None,
                progressbar=False,
                n_workers=2,
            ),
        )
    with pytest.raises(ValueError, match="reraise"):
        # hit without ProcessPool
        list(
            multiprocessing_imap(
                foo,
                range(size),
                power=None,
                progressbar=False,
                n_workers=1,
            ),
        )
