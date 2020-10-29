import numpy as np
import pandas as pd

import mapply


def test_df_mapply():
    mapply.init(progressbar=False, chunk_size=1)

    np.random.seed(1)
    df = pd.DataFrame(
        np.random.randint(0, 300, size=(int(2000), 4)), columns=list("ABCD")
    )

    # axis as positional arg
    df["totals"] = df.mapply(lambda x: x.A + x.B, "columns")

    # same output along both axes
    pd.testing.assert_frame_equal(
        df.apply(lambda x: x ** 2),
        df.mapply(lambda x: x ** 2),
    )
    pd.testing.assert_frame_equal(
        df.mapply(lambda x: x ** 2, axis=0),
        df.mapply(lambda x: x ** 2, axis=1),
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
    fn = lambda x: [x.A, x.B]  # noqa:E731
    pd.testing.assert_frame_equal(
        df.apply(fn, axis=1, result_type="expand"),
        df.mapply(fn, axis=1, result_type="expand"),
    )

    # max_chunks_per_worker=0
    mapply.init(progressbar=False, chunk_size=1, max_chunks_per_worker=0)
    pd.testing.assert_frame_equal(
        df.apply(lambda x: x ** 2),
        df.mapply(lambda x: x ** 2),
    )

    # n_workers=1
    mapply.init(progressbar=False, chunk_size=1, n_workers=1)
    pd.testing.assert_frame_equal(
        df.apply(lambda x: x ** 2),
        df.mapply(lambda x: x ** 2),
    )


def test_series_mapply():
    # chunk_size>1
    mapply.init(progressbar=False, chunk_size=5)

    fn = lambda x: x ** 2  # noqa:E731
    series = pd.Series(range(100))

    # convert_dtype=False
    pd.testing.assert_series_equal(
        series.apply(fn, convert_dtype=False),
        series.mapply(fn, convert_dtype=False),
    )

    series = pd.Series({"a": list(range(100))})

    assert isinstance(series.mapply(lambda x: sum(x))[0], np.int64)
