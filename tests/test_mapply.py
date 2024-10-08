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
import numpy as np
import pandas as pd
import pytest

import mapply


def test_df_mapply():
    """Assert DataFrame behaviour is equivalent."""
    mapply.init(progressbar=False, chunk_size=1)

    np.random.seed(1)  # noqa: NPY002
    df = pd.DataFrame(  # noqa: PD901
        np.random.randint(0, 300, size=(2000, 4)),  # noqa: NPY002
        columns=list("ABCD"),
    )

    # test GroupBy
    df["E"] = [0] * (len(df) // 2) + [1] * (len(df) - len(df) // 2)
    pd.testing.assert_frame_equal(
        df.groupby("E").apply(sum),
        df.groupby("E").mapply(sum),
    )
    # empty GroupBy
    pd.testing.assert_frame_equal(
        df.iloc[:0].groupby("E").apply(sum),
        df.iloc[:0].groupby("E").mapply(sum),
    )

    # axis as positional arg
    df["totals"] = df.mapply(lambda x: x.A + x.B, "columns")

    # same output along both axes
    pd.testing.assert_frame_equal(
        df.apply(lambda x: x**2),
        df.mapply(lambda x: x**2),
    )
    pd.testing.assert_frame_equal(
        df.mapply(lambda x: x**2, axis=0),
        df.mapply(lambda x: x**2, axis=1),
    )

    # vectorized
    pd.testing.assert_series_equal(
        df.apply(sum),
        df.mapply(np.sum, raw=True),
    )
    pd.testing.assert_series_equal(
        df.apply(sum, axis=1),
        df.mapply(np.sum, raw=True, axis=1),
    )

    # result_type kwarg
    def fn(x):
        return [x.A, x.B]

    pd.testing.assert_frame_equal(
        df.apply(fn, axis=1, result_type="expand"),
        df.mapply(fn, axis=1, result_type="expand"),
    )

    # max_chunks_per_worker=0  # noqa: ERA001
    mapply.init(progressbar=False, chunk_size=1, max_chunks_per_worker=0)
    pd.testing.assert_frame_equal(
        df.apply(lambda x: x**2),
        df.mapply(lambda x: x**2),
    )

    # n_workers=1  # noqa: ERA001
    mapply.init(progressbar=False, chunk_size=1, n_workers=1)
    pd.testing.assert_frame_equal(
        df.apply(lambda x: x**2),
        df.mapply(lambda x: x**2),
    )
    pd.testing.assert_frame_equal(
        df.groupby("E").apply(sum),
        df.groupby("E").mapply(sum),
    )

    # not all result chunks have equal size (trailing chunk)
    mapply.init(progressbar=False, chunk_size=100, n_workers=2)
    df = pd.DataFrame(np.random.randint(2, size=(5, 201)))  # noqa: NPY002, PD901
    pd.testing.assert_series_equal(
        df.apply(np.var),
        df.mapply(np.var),
    )

    # concat for only one result
    mapply.init(progressbar=False, chunk_size=100, n_workers=2)
    df = pd.DataFrame(list(range(1, 200)))  # (199, 1)  # noqa: PD901
    pd.testing.assert_series_equal(
        df.apply(sum, axis=1),
        df.mapply(sum, axis=1),
    )

    # single row dataframe turns into multi row dataframe with same columns
    mapply.init(progressbar=False, chunk_size=2, n_workers=2)
    pd.testing.assert_frame_equal(
        df.T.apply(lambda y: pd.Series(np.arange(10))),  # noqa: ARG005
        df.T.mapply(lambda y: pd.Series(np.arange(10))),  # noqa: ARG005
    )


def test_series_mapply():
    """Assert Series behaviour is equivalent."""
    # chunk_size>1
    mapply.init(progressbar=False, chunk_size=5)

    def fn(x):
        return x**2

    series = pd.Series(range(100))

    with pytest.raises(ValueError, match="Passing axis=1 is not allowed for Series"):
        series.mapply(fn, axis=1)

    # convert_dtype=False  # noqa: ERA001
    pd.testing.assert_series_equal(
        series.apply(fn, convert_dtype=False),
        series.mapply(fn, convert_dtype=False),
    )

    series = pd.Series({"a": list(range(100))})

    assert isinstance(series.mapply(lambda x: sum(x))[0], np.int64)
